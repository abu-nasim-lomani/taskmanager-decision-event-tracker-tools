# events/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Event
from .forms import EventForm
from core.utils import is_privileged_user
from django.core.exceptions import PermissionDenied

@login_required
def event_list(request):
    events = Event.objects.all().order_by('start_date') 
    return render(request, 'events/event_list.html', {'events': events})

@login_required
def event_create(request):
    if not is_privileged_user(request.user):
        raise PermissionDenied
    
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            form.save_m2m() # Important for ManyToManyFields
            return redirect('event_list')
    else:
        form = EventForm()
    
    return render(request, 'events/event_form.html', {'form': form})