import asyncio
import os
import django
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from django.conf import settings
from main.models import UserProfile
from asgiref.sync import sync_to_async  # Для обгортання синхронних функцій у асинхронний код

# Налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Help.settings')
django.setup()

# Ініціалізація бота та диспетчера
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
router = Router()
dp = Dispatcher()
dp.include_router(router)




# Хендлер команди /start
@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привіт! Введіть ваш секретний ключ.")

# Хендлер для перевірки тексту
@router.message()
async def handle_message(message: types.Message):
    # Обгортання доступу до бази даних у sync_to_async
    user_profile = await sync_to_async(UserProfile.objects.filter(secret_key=message.text).first)()
    if user_profile:
        if user_profile.telegram_group_id:
            # Якщо група вже зареєстрована
            await message.answer("✅ Ваша група вже зареєстрована! Ви можете отримувати сповіщення.")
        else:
            # Реєстрація групи
            user_profile.telegram_group_id = message.chat.id
            await sync_to_async(user_profile.save)()  # Зберігаємо групу
            await message.answer("✅ Групу успішно зареєстровано! Ви тепер будете отримувати сповіщення.")
    else:
        await message.answer("❌ Невірний секретний ключ. Спробуйте ще раз.")

# Головна функція для запуску бота
async def main():
    print("Telegram Bot запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
