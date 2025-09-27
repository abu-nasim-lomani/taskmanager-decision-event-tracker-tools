from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from .models import Meeting, Task
from accounts.models import User
from .utils import is_privileged_user
from django.contrib import messages
from .forms import MeetingCreateForm, MeetingUpdateForm, TaskCreateForm, TaskUpdateForm
import datetime

@login_required
def meeting_list(request):
    if is_privileged_user(request.user):
        all_meetings = Meeting.objects.all()
    else:
        all_meetings = Meeting.objects.filter(participants=request.user).distinct()

    now = timezone.now()
    
    # Separate meetings into upcoming and past
    upcoming_meetings = all_meetings.filter(meeting_time__gte=now).order_by('meeting_time')
    past_meetings = all_meetings.filter(meeting_time__lt=now).order_by('-meeting_time')

    # Paginate ONLY the past meetings
    paginator = Paginator(past_meetings, 10)
    page_number = request.GET.get('page')
    past_meetings_page = paginator.get_page(page_number)

    # Calculate stats
    total_meetings_count = all_meetings.count()
    completed_meetings_count = all_meetings.filter(status=Meeting.MeetingStatus.COMPLETED).count()
    total_tasks_count = Task.objects.filter(meeting__in=all_meetings).count()
    avg_duration_data = all_meetings.aggregate(avg_duration=Avg('duration'))
    avg_duration = avg_duration_data.get('avg_duration')

    context = {
        'upcoming_meetings': upcoming_meetings,
        'meetings': past_meetings_page, # This now contains only PAST meetings
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
    if not is_privileged_user(request.user):
        raise PermissionDenied
    if request.method == 'POST':
        form = MeetingCreateForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            # Combine date and time
            date = form.cleaned_data.get("meeting_date")
            time = form.cleaned_data.get("meeting_start_time")
            meeting.meeting_time = datetime.datetime.combine(date, time)
            meeting.save()
            form.save_m2m()  # Save participants
            meeting.participants.add(request.user)
            messages.success(request, f"Meeting '{meeting.title}' created successfully.")
            return redirect('meeting_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = MeetingCreateForm()
    return render(request, 'core/meeting_form.html', {'form': form})


@login_required
def meeting_update(request, pk):
    if not is_privileged_user(request.user):
        raise PermissionDenied
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        form = MeetingUpdateForm(request.POST, instance=meeting)
        if form.is_valid():
            updated_meeting = form.save(commit=False)
            # Combine date and time
            date = form.cleaned_data.get("meeting_date")
            time = form.cleaned_data.get("meeting_start_time")
            updated_meeting.meeting_time = datetime.datetime.combine(date, time)
            updated_meeting.save()
            form.save_m2m()
            messages.success(request, f"Meeting '{updated_meeting.title}' updated successfully.")
            return redirect('meeting_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = MeetingUpdateForm(instance=meeting)
    return render(request, 'core/meeting_form.html', {'form': form, 'meeting': meeting})

@login_required
@require_POST
def meeting_delete(request, pk):
    if not is_privileged_user(request.user): raise PermissionDenied
    meeting = get_object_or_404(Meeting, pk=pk)
    meeting.delete()
    return redirect('meeting_list')

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    is_privileged = is_privileged_user(request.user)
    if not (is_privileged or request.user == task.owner): raise PermissionDenied
    
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
    if not is_privileged_user(request.user): raise PermissionDenied
    task = get_object_or_404(Task, pk=pk)
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

@login_required
def management_report(request, manager_id=None):
    if not is_privileged_user(request.user):
        raise PermissionDenied

    meetings = Meeting.objects.all().order_by('-meeting_time')
    selected_manager = None

    if manager_id:
        meetings = meetings.filter(tasks__owner__id=manager_id).distinct()
        selected_manager = get_object_or_404(User, id=manager_id)

    context = {
        'meetings': meetings,
        'selected_manager': selected_manager,
    }
    return render(request, 'core/management_report.html', context)