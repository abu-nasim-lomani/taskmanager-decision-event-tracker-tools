# core/views.py
from django.shortcuts import render, get_object_or_404
from .models import Meeting

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