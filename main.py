import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import config

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

# Главное меню
main_keyboard = InlineKeyboardMarkup(row_width=1)
main_keyboard.add(
    InlineKeyboardButton("🍴 Открыть приложение", web_app=WebAppInfo(url="https://your-hosting-url.com"))
)

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в наш ресторан! 🍕\n\nНажмите кнопку ниже, чтобы открыть приложение:",
        reply_markup=main_keyboard
    )

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)