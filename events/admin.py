# events/admin.py
from django.contrib import admin
from .models import Event, Invitation

class InvitationInline(admin.TabularInline):
    model = Invitation
    extra = 1

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_datetime', 'created_by')
    search_fields = ('title', 'description')
    list_filter = ('start_datetime',)
    inlines = [InvitationInline]

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('event', 'invitee', 'status')
    list_filter = ('status',)