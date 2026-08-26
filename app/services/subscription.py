from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from app.services.settings_store import required_channel


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    channel = required_channel()
    if not channel:
        return True
    try:
        member = await bot.get_chat_member(channel, user_id)
        return member.status in {"member", "administrator", "creator"}
    except TelegramBadRequest:
        return False
