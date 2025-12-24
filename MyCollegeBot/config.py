import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
# Превращаем строку с ID админов в список чисел
ADMIN_IDS = [int(id_str) for id_str in os.getenv("ADMIN_IDS", "").split(",") if id_str]
DATABASE_URL = "sqlite+aiosqlite:///bot_database.db"