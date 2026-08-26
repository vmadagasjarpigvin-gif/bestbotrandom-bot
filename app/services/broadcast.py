import asyncio
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest, TelegramRetryAfter
from app.db import participant_ids
from app.raw_api import send_styled_message, styled_button
from app.services.settings_store import broadcast_delay, prize_contact


async def broadcast(bot: Bot, admin_chat_id: int, text: str, only_subscribed: bool = True) -> dict:
    ids = participant_ids(only_subscribed=only_subscribed)
    total = len(ids)
    sent = failed = 0
    await bot.send_message(admin_chat_id, f"✅ Рассылка поставлена в очередь.\n👥 Будет отправлено: {total}")
    for user_id in ids:
        try:
            await send_styled_message(
                user_id,
                text,
                inline_keyboard=[[styled_button("связаться", url=f"https://t.me/{prize_contact().lstrip('@')}", style="primary")]],
            )
            sent += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
        except (TelegramForbiddenError, TelegramBadRequest, RuntimeError):
            failed += 1
        await asyncio.sleep(broadcast_delay())
    report = {"total": total, "sent": sent, "failed": failed}
    await bot.send_message(admin_chat_id, f"📬 Рассылка завершена\nВсего: {total}\nОтправлено: {sent}\nОшибок: {failed}")
    return report
