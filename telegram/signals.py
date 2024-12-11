import asyncio
import secrets
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from main.models import Task, UserProfile
from .utils import send_telegram_message
import logging

logger = logging.getLogger(__name__)

def to_http(url: str) -> str:
    if url.startswith("https://"):
        return url.replace("https://", "http://", 1)
    return url

# Сигнал для сповіщення при створенні задачі
@receiver(post_save, sender=Task)
def notify_on_task_creation(sender, instance, created, **kwargs):
    if created:  # Перевіряємо, чи це нова задача
        current_site = Site.objects.get_current()
        task_url = to_http(f"https://{current_site.domain}{instance.get_absolute_url()}")  # Використовуємо to_http

        # Відправляємо повідомлення всім виконавцям
        for user in instance.assigned_to.all():
            if user.profile.telegram_group_id:
                message = (
                    f"🔔 Нова задача призначена вам:\n"
                    f"📋 Номер: {instance.task_number}\n"
                    f"📌 Назва: {instance.title}\n"
                    f"🧑‍💻 Автор: {instance.assigned_by.username}\n"
                    f"📅 Дедлайн: {instance.deadline.strftime('%Y-%m-%d %H:%M')}\n"
                    f"🔗 Деталі: {task_url}"
                )
                asyncio.run(send_telegram_message(user.profile.telegram_group_id, message))


# Сигнал для сповіщення при зміні виконавців
@receiver(m2m_changed, sender=Task.assigned_to.through)
def notify_assigned_users(sender, instance, action, **kwargs):
    if action == "post_add":  # Виконавці додані
        current_site = Site.objects.get_current()
        task_url = to_http(f"https://{current_site.domain}{instance.get_absolute_url()}")  # Використовуємо to_http

        # Сповіщення нових виконавців
        for user in instance.assigned_to.all():
            if user.profile.telegram_group_id:
                message = (
                    f"🔔 Вас призначено на нову задачу:\n"
                    f"📋 Номер: {instance.task_number}\n"
                    f"📌 Назва: {instance.title}\n"
                    f"🧑‍💻 Автор: {instance.assigned_by.username}\n"
                    f"📅 Дедлайн: {instance.deadline.strftime('%Y-%m-%d %H:%M')}\n"
                    f"🔗 Деталі: {task_url}"
                )
                asyncio.run(send_telegram_message(user.profile.telegram_group_id, message))


# Сигнал для створення профілю користувача
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        secret_key = secrets.token_hex(16)  # Генерація унікального секретного ключа
        UserProfile.objects.create(user=instance, secret_key=secret_key)
