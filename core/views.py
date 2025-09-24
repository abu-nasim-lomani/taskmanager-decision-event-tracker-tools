from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from .models import Meeting, Task
from accounts.models import User
from .forms import MeetingForm, TaskCreateForm, TaskUpdateForm

# Helper function
def is_privileged_user(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'MANAGEMENT')

# Meeting & Dashboard Views
@login_required
def meeting_list(request):
    if is_privileged_user(request.user):
        all_meetings = Meeting.objects.all()
    else:
        all_meetings = Meeting.objects.filter(participants=request.user)
    
    total_meetings_count = all_meetings.count()
    completed_meetings_count = all_meetings.filter(status=Meeting.MeetingStatus.COMPLETED).count()
    total_tasks_count = Task.objects.count()
    avg_duration_data = all_meetings.aggregate(avg_duration=Avg('duration'))
    avg_duration = avg_duration_data.get('avg_duration')

    ordered_meetings = all_meetings.order_by('-meeting_time')
    paginator = Paginator(ordered_meetings, 10)
    page_number = request.GET.get('page')
    meetings_page = paginator.get_page(page_number)

    context = {
        'meetings': meetings_page,
        'total_meetings_count': total_meetings_count,
        'completed_meetings_count': completed_meetings_count,
        'total_tasks_count': total_tasks_count,
        'avg_duration': avg_duration,
    }
    return render(request, 'core/meeting_list.html', context)

@login_required
def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    is_privileged = is_privileged_user(request.user)

    if request.method == 'POST':
        form = TaskCreateForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.meeting = meeting
            if not is_privileged:
                task.owner = request.user
            task.save()
            return redirect('meeting_detail', pk=meeting.pk)
    else:
        form = TaskCreateForm()
        if not is_privileged:
            if 'owner' in form.fields:
                form.fields.pop('owner')

    context = {'meeting': meeting, 'form': form, 'is_privileged': is_privileged}
    return render(request, 'core/meeting_detail.html', context)

@login_required
def meeting_create(request):
    if not is_privileged_user(request.user): raise PermissionDenied
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save()
            meeting.participants.add(request.user)
            return redirect('meeting_list')
    else:
        form = MeetingForm()
    return render(request, 'core/meeting_form.html', {'form': form})

@login_required
def meeting_update(request, pk):
    if not is_privileged_user(request.user): raise PermissionDenied
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            return redirect('meeting_list')
    else:
        form = MeetingForm(instance=meeting)
    return render(request, 'core/meeting_form.html', {'form': form, 'meeting': meeting})

@login_required
@require_POST
def meeting_delete(request, pk):
    if not is_privileged_user(request.user): raise PermissionDenied
    meeting = get_object_or_404(Meeting, pk=pk)
    meeting.delete()
    return redirect('meeting_list')

# Task & User-Specific Views
@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if not (is_privileged_user(request.user) or request.user == task.owner):
        raise PermissionDenied
    
    if request.method == 'POST':
        form = TaskUpdateForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('my_tasks')
    else:
        form = TaskUpdateForm(instance=task, user=request.user)
    
    context = {'form': form, 'task': task}
    return render(request, 'core/task_update.html', context)

@login_required
@require_POST
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if not (is_privileged_user(request.user) or request.user == task.owner): raise PermissionDenied
    meeting_pk = task.meeting.pk
    task.delete()
    return redirect('meeting_detail', pk=meeting_pk)

@login_required
def my_tasks(request):
    all_user_tasks = Task.objects.filter(owner=request.user)
    
    pending_tasks = all_user_tasks.filter(status=Task.StatusChoices.PENDING).order_by('due_date')
    inprogress_tasks = all_user_tasks.filter(status=Task.StatusChoices.IN_PROGRESS).order_by('due_date')
    blocked_tasks = all_user_tasks.filter(status=Task.StatusChoices.BLOCKED).order_by('due_date')
    completed_tasks = all_user_tasks.filter(status=Task.StatusChoices.COMPLETED).order_by('-updated_at')

    context = {
        'pending_tasks': pending_tasks,
        'inprogress_tasks': inprogress_tasks,
        'blocked_tasks': blocked_tasks,
        'completed_tasks': completed_tasks,
    }
    return render(request, 'core/my_tasks.html', context)

@login_required
def management_dashboard(request):
    if not is_privileged_user(request.user): raise PermissionDenied
    managers = User.objects.filter(role='MANAGER').annotate(
        total_tasks=Count('task_owned'),
        completed_tasks=Count('task_owned', filter=Q(task_owned__status=Task.StatusChoices.COMPLETED)),
        incomplete_tasks=Count('task_owned', filter=~Q(task_owned__status=Task.StatusChoices.COMPLETED))
    ).order_by('username')
    context = {'managers': managers}
    return render(request, 'core/management_dashboard.html', context)