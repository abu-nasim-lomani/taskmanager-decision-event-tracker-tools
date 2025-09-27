from django import forms
from .models import Meeting, Task
from accounts.models import User

# This form will be used for CREATING new meetings
class MeetingCreateForm(forms.ModelForm):
    DURATION_CHOICES = [(30, '30 minutes'), (60, '60 minutes'), (90, '90 minutes'), (120, '120 minutes')]
    duration = forms.ChoiceField(choices=DURATION_CHOICES, widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}))
    meeting_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}))
    meeting_start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}))

    class Meta:
        model = Meeting
        # Note: 'status' is NOT included here
        fields = ['title', 'duration', 'meeting_type', 'participants']
        labels = {'title': 'Meeting Title', 'duration': 'Duration', 'meeting_type': 'Meeting Type', 'participants': 'Invite Participants'}
        widgets = {
            'meeting_type': forms.RadioSelect(attrs={'class': 'sr-only peer'}),
            'participants': forms.CheckboxSelectMultiple(),
        }

# This form will be used for UPDATING existing meetings
class MeetingUpdateForm(forms.ModelForm):
    DURATION_CHOICES = [(30, '30 minutes'), (60, '60 minutes'), (90, '90 minutes'), (120, '120 minutes')]
    duration = forms.ChoiceField(choices=DURATION_CHOICES, widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}))
    meeting_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}))
    meeting_start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}))

    class Meta:
        model = Meeting
        # Note: 'status' IS included here
        fields = ['title', 'duration', 'meeting_type', 'participants', 'status']
        labels = {'title': 'Meeting Title', 'duration': 'Duration', 'meeting_type': 'Meeting Type', 'participants': 'Invite Participants', 'status': 'Meeting Status'}
        widgets = {
            'meeting_type': forms.RadioSelect(attrs={'class': 'sr-only peer'}),
            'participants': forms.CheckboxSelectMultiple(),
            'status': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['meeting_date'].initial = self.instance.meeting_time.date()
            self.fields['meeting_start_time'].initial = self.instance.meeting_time.time()


# --- Task Forms (remain unchanged) ---
class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'owner', 'due_date', 'priority']
        labels = {'owner': 'Assign To', 'due_date': 'Due Date'}
        widgets = {
            'title': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'owner': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'priority': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'owner', 'due_date', 'priority', 'status']
        labels = {'owner': 'Assign To', 'due_date': 'Due Date', 'status': 'Current Status'}
        widgets = {
            'title': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'owner': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'priority': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'status': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
