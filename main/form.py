from django import forms
from django.contrib.auth.models import User
from django.utils.dateparse import parse_datetime

from .models import Task, Message


class TaskForm(forms.ModelForm):
    assigned_to = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': 5,
        }),
        required=True,
    )

    class Meta:
        model = Task
        fields = ['title', 'assigned_to', 'priority', 'deadline', 'status', 'description']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'text',  # Для інтеграції з Flatpickr
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data['deadline']
        if isinstance(deadline, str):  # Якщо Flatpickr повертає строку
            try:
                deadline = parse_datetime(deadline)
            except ValueError:
                raise forms.ValidationError("Некоректний формат дати.")
        return deadline