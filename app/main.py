import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import settings
from app.db import init_db
from app.handlers import user, admin
from app.services import settings_store

async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()
    settings_store.init_settings()
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(user.router)
    dp.include_router(admin.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
