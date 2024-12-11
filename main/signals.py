from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TaskPerformer, Task, UserProfile
from django.utils.timezone import now

@receiver(post_save, sender=TaskPerformer)
def update_task_dates(sender, instance, **kwargs):
    task = instance.task
    performers = task.performers.all()

    # Якщо всі виконавці почали виконання
    if all(p.status == 'in_progress' for p in performers):
        if not task.started_at:
            task.started_at = now()

    # Якщо всі виконавці завершили
    if all(p.status == 'completed' for p in performers):
        if not task.finished_at:
            task.finished_at = now()

    # Оновлюємо статус задачі
    if all(p.status == 'completed' for p in performers):
        task.status = 'completed'
    elif any(p.status == 'in_progress' for p in performers):
        task.status = 'in_progress'

    task.save()


