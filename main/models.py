import uuid

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


def generate_task_number(instance):
    task_count = Task.objects.count() + 1  # Лічильник задач
    return f"T-{str(task_count).zfill(9)}"

class Task(models.Model):
    task_number = models.CharField(max_length=12, unique=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    assigned_to = models.ManyToManyField(User, through='TaskPerformer', related_name='assigned_to_tasks')
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)  # Дата виконання задачі (якщо всі почали)
    finished_at = models.DateTimeField(null=True, blank=True)  # Дата завершення задачі (якщо всі завершили)
    priority_choices = [
        ('basic', 'Базовий'),
        ('non_urgent', 'Нетерміновий'),
        ('urgent', 'Терміновий'),
    ]
    priority = models.CharField(max_length=20, choices=priority_choices, default='basic')
    status_choices = [
        ('not_started', 'Не розпочато'),
        ('in_progress', 'Виконується'),
        ('completed', 'Завершено'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='not_started')

    def save(self, *args, **kwargs):
        if not self.task_number:
            self.task_number = generate_task_number(self)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

class TaskPerformer(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='performers')
    performer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    started_at = models.DateTimeField(null=True, blank=True)  # Дата коли взяв на виконання
    completed_at = models.DateTimeField(null=True, blank=True)  # Дата коли завершив
    status_choices = [
        ('not_started', 'Не розпочато'),
        ('in_progress', 'Виконується'),
        ('completed', 'Завершено'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='not_started')

    def __str__(self):
        return f"{self.performer.username} - {self.task.title}"

class Message(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)  # Поле для файлів


    def __str__(self):
        return f"Message by {self.author.username} on {self.created_at}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    secret_key = models.CharField(max_length=50, unique=True)
    telegram_group_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.username



class DeadlineHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='deadline_histories')
    old_deadline = models.DateTimeField()
    new_deadline = models.DateTimeField()
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Deadline changed for {self.task.title} on {self.changed_at}"