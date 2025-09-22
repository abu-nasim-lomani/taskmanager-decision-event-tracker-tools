# core/models.py

from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.conf import settings

class Meeting(models.Model):
    class MeetingType(models.TextChoices):
        TEAM = "TEAM", "Team"
        PROJECT = "PROJECT", "Project"
        BRAINSTORM = "BRAINSTORM", "Brainstorm"
        REVIEW = "REVIEW", "Review"

    title = models.CharField(max_length=200)
    meeting_time = models.DateTimeField(default=timezone.now)
    duration = models.IntegerField(default=60, help_text="Duration in minutes")
    meeting_type = models.CharField(max_length=20, choices=MeetingType.choices, default=MeetingType.TEAM)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} on {self.meeting_time.strftime('%b %d, %Y at %I:%M %p')}"
    
    def get_absolute_url(self):
        return reverse('meeting_detail', kwargs={'pk': self.pk})

class Task(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        BLOCKED = "BLOCKED", "Blocked"

    class PriorityChoices(models.TextChoices):
        HIGH = "HIGH", "High"
        MEDIUM = "MEDIUM", "Medium"
        LOW = "LOW", "Low"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='tasks')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='task_owned' # <-- এই অংশটি যোগ করা হয়েছে
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    priority = models.CharField(max_length=20, choices=PriorityChoices.choices, default=PriorityChoices.MEDIUM)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title