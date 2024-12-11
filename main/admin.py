from django.contrib import admin
from .models import Task, TaskPerformer, Message

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_number', 'title', 'status', 'priority', 'deadline', 'created_at', 'started_at', 'finished_at')
    list_filter = ('status', 'priority', 'deadline')
    search_fields = ('task_number', 'title', 'description')
    ordering = ('-created_at',)

@admin.register(TaskPerformer)
class TaskPerformerAdmin(admin.ModelAdmin):
    list_display = ('task', 'performer', 'status', 'started_at', 'completed_at')
    list_filter = ('status',)
    search_fields = ('task__title', 'performer__username')
    ordering = ('task',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'content', 'created_at')
    search_fields = ('task__title', 'author__username', 'content')
    ordering = ('-created_at',)
