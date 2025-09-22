# core/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Avg
from django.utils import timezone
from .models import Meeting, Task
from .forms import MeetingForm, TaskForm

# =================================
# Meeting Views
# =================================

def meeting_list(request):
    all_meetings = Meeting.objects.all()
    
    # Calculate stats before pagination
    total_meetings_count = all_meetings.count()
    completed_meetings_count = all_meetings.filter(meeting_time__lt=timezone.now()).count()
    total_tasks_count = Task.objects.count()
    
    # Calculate average duration
    avg_duration_data = all_meetings.aggregate(avg_duration=Avg('duration'))
    avg_duration = avg_duration_data.get('avg_duration')

    # Paginate the ordered list of meetings
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

def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.meeting = meeting
            task.save()
            return redirect('meeting_detail', pk=meeting.pk)
    else:
        form = TaskForm()
    return render(request, 'core/meeting_detail.html', {'meeting': meeting, 'form': form})

def meeting_create(request):
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('meeting_list')
    else:
        form = MeetingForm()
    return render(request, 'core/meeting_form.html', {'form': form})

def meeting_update(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            return redirect('meeting_list')
    else:
        form = MeetingForm(instance=meeting)
    return render(request, 'core/meeting_form.html', {'form': form, 'meeting': meeting})

@require_POST
def meeting_delete(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    meeting.delete()
    return redirect('meeting_list')


# =================================
# Task Views
# =================================

def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('meeting_detail', pk=task.meeting.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'core/task_update.html', {'form': form, 'task': task})

@require_POST
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    meeting_pk = task.meeting.pk
    task.delete()
    return redirect('meeting_detail', pk=meeting_pk)