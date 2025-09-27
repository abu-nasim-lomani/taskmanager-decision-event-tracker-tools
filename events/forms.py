import datetime
from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    # Separate fields for date and time for better browser compatibility and styling
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'})
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'})
    )
    end_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'})
    )

    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'participants']
        
        labels = {
            'title': 'Event Title',
            'description': 'Description',
            'location': 'Location (e.g., Conference Room A)',
            'participants': 'Invite Participants'
        }

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 lg:text-lg'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
            }),
            'location': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
            }),
            'participants': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.start_datetime:
                self.fields['start_date'].initial = self.instance.start_datetime.date()
                self.fields['start_time'].initial = self.instance.start_datetime.time()
            if self.instance.end_datetime:
                self.fields['end_date'].initial = self.instance.end_datetime.date()
                self.fields['end_time'].initial = self.instance.end_datetime.time()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        start_time = cleaned_data.get("start_time")
        end_date = cleaned_data.get("end_date")
        end_time = cleaned_data.get("end_time")

        if start_date and start_time:
            cleaned_data['start_datetime'] = datetime.datetime.combine(start_date, start_time)
        
        if end_date and end_time:
            cleaned_data['end_datetime'] = datetime.datetime.combine(end_date, end_time)
            if cleaned_data.get('start_datetime') and cleaned_data['end_datetime'] < cleaned_data['start_datetime']:
                self.add_error('end_date', 'End time cannot be before the start time.')
        elif end_date and not end_time:
            self.add_error('end_time', 'An end time is required if an end date is provided.')
        elif end_time and not end_date:
            self.add_error('end_date', 'An end date is required if an end time is provided.')
            
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.start_datetime = self.cleaned_data.get('start_datetime')
        instance.end_datetime = self.cleaned_data.get('end_datetime')
        if commit:
            instance.save()
            self.save_m2m()
        return instance

