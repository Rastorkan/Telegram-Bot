from dotenv import load_dotenv
load_dotenv()
import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# Получаем переменные окружения
API_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
if not API_TOKEN:
    raise ValueError("Переменная окружения TELEGRAM_TOKEN не установлена. Добавьте её в Secrets на Replit.")
if not TMDB_API_KEY:
    raise ValueError("Переменная окружения TMDB_API_KEY не установлена. Добавьте её в Secrets на Replit.")

# Создаем объекты бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Команда /start с кнопкой для получения списка
@router.message(Command("start"))
async def send_welcome(message: types.Message):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Показать список", callback_data="show_list")]
    ])
    await message.answer("Привет! Я бот для списка фильмов и сериалов. Нажми кнопку, чтобы получить список из TMDb.", reply_markup=markup)

# Функция для получения списка с TMDb
async def get_tmdb_list(list_id: str) -> dict:
    url = f"https://api.themoviedb.org/3/list/{list_id}?api_key={TMDB_API_KEY}&language=ru-RU"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Обработчик нажатия на кнопку "Показать список"
@router.callback_query(lambda call: call.data == "show_list")
async def show_tmdb_list(callback: types.CallbackQuery):
    # Замените "YOUR_LIST_ID" на фактический ID вашего списка в TMDb
    list_id = "8524721"
    data = await get_tmdb_list(list_id)

    message_text = "Список фильмов/сериалов:\n"
    if "items" in data:
        for item in data["items"]:
            title = item.get("title") or item.get("name", "Без названия")
            message_text += f"• {title}\n"
    else:
        message_text = "Ошибка: не удалось получить список. Проверьте правильность ID и API-ключа."

    await callback.message.answer(message_text)
    await callback.answer()

# Регистрируем роутер в диспетчере
dp.include_router(router)

# Основная функция запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
