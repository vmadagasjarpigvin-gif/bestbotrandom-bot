import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import settings
from app.db import init_db
from app.handlers import user, admin
from app.services import settings_store


async def health(_request: web.Request) -> web.Response:
    return web.Response(text="ok")


async def start_health_server() -> None:
    port = int(os.getenv("PORT", "10000"))
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info("Health server started on port %s", port)


async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()
    settings_store.init_settings()
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(user.router)
    dp.include_router(admin.router)
    await start_health_server()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
