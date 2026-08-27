import asyncio
from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from app.db import upsert_participant, mark_auto_win_sent, auto_win_was_sent, get_participant
from app.keyboards.user import start_keyboard, subscribe_keyboard, contact_keyboard
from app.raw_api import send_styled_message
from app.services.subscription import is_subscribed
from app.services.settings_store import format_template, auto_win_delay, auto_win_enabled

router = Router()


@router.message(CommandStart())
async def start(message: Message, command: CommandObject):
    referrer_id = None
    if command.args and command.args.startswith("ref"):
        try:
            referrer_id = int(command.args[3:])
        except ValueError:
            referrer_id = None
    if referrer_id and referrer_id != message.from_user.id:
        # Сохраняем источник до проверки подписки; шанс начислится после успешной регистрации.
        upsert_participant(message.from_user.id, message.from_user.username, message.from_user.first_name, False, referrer_id)
    text = format_template("welcome_text", first_name=message.from_user.first_name or "участник", user_id=str(message.from_user.id))
    await send_styled_message(message.chat.id, text, inline_keyboard=start_keyboard()["inline_keyboard"])


@router.callback_query(F.data == "join_contest")
async def join_contest(callback: CallbackQuery):
    await send_styled_message(
        callback.message.chat.id,
        format_template("subscribe_text"),
        inline_keyboard=subscribe_keyboard()["inline_keyboard"],
    )
    await callback.answer()


async def delayed_auto_win(bot: Bot, user_id: int):
    delay = auto_win_delay()
    if delay > 0:
        await asyncio.sleep(delay)
    if not auto_win_enabled() or auto_win_was_sent(user_id):
        return
    mark_auto_win_sent(user_id)
    await send_styled_message(user_id, format_template("auto_win_text"), inline_keyboard=contact_keyboard("winner_button_text"))


@router.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery, bot: Bot):
    ok = await is_subscribed(bot, callback.from_user.id)
    existing = get_participant(callback.from_user.id)
    referrer_id = existing.get("referred_by") if existing else None
    upsert_participant(callback.from_user.id, callback.from_user.username, callback.from_user.first_name, ok, referrer_id)
    if ok:
        current = get_participant(callback.from_user.id) or {}
        await send_styled_message(
            callback.message.chat.id,
            format_template(
                "registered_text",
                user_id=str(callback.from_user.id),
                chances=str(current.get("chances", 1)),
                referral_count=str(current.get("referral_count", 0)),
            ),
        )
        # Авто-отправка сообщения «Поздравляем! Подведены итоги конкурса!» отключена.
        # Победные сообщения теперь отправляются только вручную из админки/рассылки.
    else:
        await callback.message.answer(format_template("not_subscribed_text"))
    await callback.answer()
