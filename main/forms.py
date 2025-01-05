
from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ['assigned_by']  # Виключаємо поле, яке заповнюється автоматично
