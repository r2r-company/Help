from django.core.management.base import BaseCommand
from telegram.bot import main  # Імпортуємо вашу асинхронну функцію main

import asyncio  # Для запуску асинхронного коду

class Command(BaseCommand):
    help = "Запуск Telegram-бота"

    def handle(self, *args, **kwargs):
        asyncio.run(main())  # Викликаємо асинхронну функцію main через asyncio.run
