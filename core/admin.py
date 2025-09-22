# core/admin.py

from django.contrib import admin
from .models import Meeting, Task

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'meeting_date', 'created_at')
    search_fields = ('title',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'meeting', 'owner', 'status', 'priority', 'due_date')
    list_filter = ('status', 'priority', 'owner', 'meeting')
    search_fields = ('title', 'description')