from aiogram import Bot
from django.conf import settings

async def send_telegram_message(chat_id: str, message: str):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
    finally:
        await bot.session.close()
