# core/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Meeting
from .forms import TaskForm
from .models import Meeting, Task 

def meeting_list(request):
    meetings = Meeting.objects.all().order_by('-meeting_date')
    context = {
        'meetings': meetings
    }
    return render(request, 'core/meeting_list.html', context)


def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    context = {
        'meeting': meeting
    }
    return render(request, 'core/meeting_detail.html', context)



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

    context = {
        'meeting': meeting,
        'form': form,
    }
    return render(request, 'core/meeting_detail.html', context)



def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('meeting_detail', pk=task.meeting.pk)
    else:
        form = TaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task
    }
    return render(request, 'core/task_update.html', context)


@require_POST
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    meeting_pk = task.meeting.pk
    task.delete()
    return redirect('meeting_detail', pk=meeting_pk)