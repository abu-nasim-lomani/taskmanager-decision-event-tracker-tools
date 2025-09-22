# core/views.py
from django.shortcuts import render
from .models import Meeting

def meeting_list(request):
    meetings = Meeting.objects.all().order_by('-meeting_date')
    context = {
        'meetings': meetings
    }
    return render(request, 'core/meeting_list.html', context)