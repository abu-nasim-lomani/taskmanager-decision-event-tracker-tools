# events/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_datetime = models.DateTimeField(default=timezone.now)
    end_datetime = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='events_created'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Invitation',
        related_name='events_participated'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # We will create this URL later
        return reverse('event_list') # Placeholder

class Invitation(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    invitee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10, 
        choices=StatusChoices.choices, 
        default=StatusChoices.PENDING
    )

    class Meta:
        unique_together = ('event', 'invitee')

    def __str__(self):
        return f"{self.invitee.username}'s invitation to {self.event.title}"