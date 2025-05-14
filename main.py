from dotenv import load_dotenv
load_dotenv()
import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# Getting environment variables
API_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
if not API_TOKEN:
    raise ValueError("The TELEGRAM_TOKEN environment variable is not set.")
if not TMDB_API_KEY:
    raise ValueError("The TMDB_API_KEY environment variable is not set.")

# Create bot and dispatcher objects
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# The /start command with a button to get the list
@router.message(Command("start"))
async def send_welcome(message: types.Message):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Show list", callback_data="show_list")]
    ])
    await message.answer("Hi, I'm a bot for a list of films and TV series. Click the button to get the list from TMDb.", reply_markup=markup)

# Function to get the list from TMDb
async def get_tmdb_list(list_id: str) -> dict:
    url = f"https://api.themoviedb.org/3/list/{list_id}?api_key={TMDB_API_KEY}&language=ru-RU"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Handler of pressing the ‘Show list’ button
@router.callback_query(lambda call: call.data == "show_list")
async def show_tmdb_list(callback: types.CallbackQuery):
    # Replace ‘YOUR_LIST_ID’ with the actual ID of your list in TMDb
    list_id = "8524721"
    data = await get_tmdb_list(list_id)

    message_text = "List of films/series:\n"
    if "items" in data:
        for item in data["items"]:
            title = item.get("title") or item.get("name", "No Name")
            message_text += f"• {title}\n"
    else:
        message_text = "Error: Failed to retrieve the list. Check if the ID and API key are correct."

    await callback.message.answer(message_text)
    await callback.answer()

# Register the router in the manager
dp.include_router(router)

# The main function of the bot launcher
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
