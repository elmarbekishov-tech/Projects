import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database.db import init_db
from handlers.user import start, profile, info, tickets
from handlers.admin import admin_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():

    import os
    if not os.path.exists("logs"):
        os.makedirs("logs")

    await init_db()
    logger.info("База данных подключена")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_routers(
        admin_handlers.router, 
        start.router,
        profile.router,
        info.router,
        tickets.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")