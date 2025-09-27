from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Event, Invitation
from .forms import EventForm
from core.utils import is_privileged_user
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.http import JsonResponse

@login_required
def event_list(request):
    events = Event.objects.all().order_by('start_datetime')
    context = {'events': events}
    return render(request, 'events/event_list.html', context)

@login_required
def event_create(request):
    if not is_privileged_user(request.user):
        raise PermissionDenied
    
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            
            # If the user confirms creation from the modal
            if 'force_create' in request.POST:
                event = form.save(commit=False)
                event.created_by = request.user
                event.save()
                form.save_m2m() # Save participants
                event.participants.add(request.user) # Add creator as a participant
                messages.success(request, f"Event '{event.title}' was created despite conflicts.")
                return redirect('event_list')

            # Initial submission: Check for conflicts
            participants = form.cleaned_data.get('participants')
            start_time = form.cleaned_data.get('start_datetime')
            end_time = form.cleaned_data.get('end_datetime') or start_time
            
            conflicting_managers = []
            if participants:
                for person in participants:
                    conflicts = Event.objects.filter(
                        participants=person,
                        start_datetime__lt=end_time,
                        end_datetime__gt=start_time
                    ).exists()
                    if conflicts:
                        conflicting_managers.append(person.username)
            
            if conflicting_managers:
                # Conflicts found, re-render the form with a warning modal
                context = {
                    'form': form,
                    'conflict_warning': True,
                    'conflicting_managers': conflicting_managers,
                }
                return render(request, 'events/event_form.html', context)
            else:
                # No conflicts, create the event directly
                event = form.save(commit=False)
                event.created_by = request.user
                event.save()
                form.save_m2m()
                event.participants.add(request.user) # Add creator as a participant
                messages.success(request, f"Event '{event.title}' was created successfully.")
                return redirect('event_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EventForm()
    
    return render(request, 'events/event_form.html', {'form': form})

@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    context = {'event': event}
    return render(request, 'events/event_detail.html', context)

@login_required
def event_update(request, pk):
    if not is_privileged_user(request.user):
        raise PermissionDenied
    
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            # Similar conflict check as in event_create
            if 'force_create' not in request.POST:
                participants = form.cleaned_data.get('participants')
                start_time = form.cleaned_data.get('start_datetime')
                end_time = form.cleaned_data.get('end_datetime') or start_time
                
                conflicting_managers = []
                if participants:
                    for person in participants:
                        conflicts = Event.objects.filter(
                            participants=person,
                            start_datetime__lt=end_time,
                            end_datetime__gt=start_time
                        ).exclude(pk=event.pk).exists()
                        if conflicts:
                            conflicting_managers.append(person.username)

                if conflicting_managers:
                    context = {
                        'form': form,
                        'event': event,
                        'conflict_warning': True,
                        'conflicting_managers': conflicting_managers,
                    }
                    return render(request, 'events/event_form.html', context)
            
            form.save()
            messages.success(request, f"Event '{event.title}' was updated successfully.")
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    
    return render(request, 'events/event_form.html', {'form': form, 'event': event})

@login_required
@require_POST
def event_delete(request, pk):
    if not is_privileged_user(request.user):
        raise PermissionDenied
    event = get_object_or_404(Event, pk=pk)
    event.delete()
    messages.success(request, f"Event '{event.title}' has been deleted.")
    return redirect('event_list')

@login_required
def my_events(request):
    invitations = Invitation.objects.filter(invitee=request.user).select_related('event')
    pending_invitations = invitations.filter(status=Invitation.StatusChoices.PENDING).count()
    accepted_invitations = invitations.filter(status=Invitation.StatusChoices.ACCEPTED).count()
    context = {
        'invitations': invitations.order_by('event__start_datetime'),
        'pending_count': pending_invitations,
        'accepted_count': accepted_invitations,
        'total_invitations': invitations.count(),
    }
    return render(request, 'events/my_events.html', context)

@login_required
@require_POST
def respond_to_invitation(request, invitation_pk, response):
    invitation = get_object_or_404(Invitation, pk=invitation_pk, invitee=request.user)
    
    if response == 'accept':
        invitation.status = Invitation.StatusChoices.ACCEPTED
        messages.success(request, f"You have accepted the invitation for '{invitation.event.title}'.")
    elif response == 'decline':
        invitation.status = Invitation.StatusChoices.REJECTED
        messages.warning(request, f"You have declined the invitation for '{invitation.event.title}'.")
    
    invitation.save()
    return redirect('my_events')

@login_required
def my_events_json(request):
    invitations = Invitation.objects.filter(invitee=request.user, status=Invitation.StatusChoices.ACCEPTED).select_related('event')
    events_data = []
    for invitation in invitations:
        event = invitation.event
        events_data.append({
            "title": event.title,
            "start": event.start_datetime.isoformat(),
            "end": event.end_datetime.isoformat() if event.end_datetime else None,
        })
    return JsonResponse(events_data, safe=False)

