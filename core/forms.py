# core/forms.py

from django import forms
from .models import Task
from accounts.models import User

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'owner', 'due_date', 'priority']
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
        labels = {
            'owner': 'Assign To',
            'due_date': 'Due Date',
        }