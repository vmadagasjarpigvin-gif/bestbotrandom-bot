import asyncio
from pathlib import Path
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, FSInputFile
from app.config import settings
from app.db import stats, export_csv, set_winner, add_runtime_admin, is_runtime_admin
from app.keyboards.admin import admin_keyboard, cancel_keyboard, settings_keyboard
from app.raw_api import send_styled_message, styled_button
from app.services.broadcast import broadcast
from app.services.settings_store import all_settings, set_setting, prize_contact, format_template

router = Router()

SETTING_LABELS = {
    "required_channel": "📣 Канал",
    "required_channel_url": "🔗 Ссылка на канал",
    "prize_contact": "👤 Куратор/контакт",
    "bot_username": "🤖 Username бота",
    "admin_usernames_extra": "👑 Username админа",
    "auto_win_enabled": "✅ Авто-победа вкл/выкл",
    "auto_win_delay_seconds": "⏳ Время до авто-победы",
    "auto_win_place": "🏆 Место",
    "welcome_text": "👋 Приветствие",
    "join_button_text": "🎉 Кнопка участия",
    "subscribe_text": "📣 Текст подписки",
    "subscribe_button_text": "📣 Кнопка подписки",
    "check_button_text": "✅ Кнопка проверки",
    "not_subscribed_text": "🔒 Текст нет подписки",
    "registered_text": "🎊 Текст регистрации",
    "auto_win_text": "🏆 Текст авто-победы",
    "manual_winner_text": "🏆 Текст ручного победителя",
    "winner_button_text": "🔘 Кнопка победителя",
    "broadcast_win_text": "📨 Текст рассылки",
    "broadcast_delay": "⏱ Задержка рассылки",
    "custom_emoji_gift": "🎁 Custom emoji gift",
    "custom_emoji_bell": "🔔 Custom emoji bell",
    "custom_emoji_lock": "🔒 Custom emoji lock",
    "custom_emoji_hello": "👋 Premium emoji 👋",
    "custom_emoji_trophy": "🏆 Premium emoji 🏆",
    "custom_emoji_party": "🎉 Premium emoji 🎉",
    "custom_emoji_envelope": "✉️ Premium emoji ✉️",
    "custom_emoji_medal": "🥇 Premium emoji 🥇",
}

CALLBACK_TO_SETTING = {f"set_{key}": key for key in SETTING_LABELS}

class AdminState(StatesGroup):
    waiting_broadcast_text = State()
    waiting_winner_id = State()
    waiting_setting_value = State()


def is_admin(user_id: int, username: str | None = None) -> bool:
    normalized = (username or "").lower().lstrip("@")
    extra_admins = {
        x.strip().lower().lstrip("@")
        for x in all_settings().get("admin_usernames_extra", "").split(",")
        if x.strip()
    }
    return (
        user_id in settings.admin_ids
        or normalized in settings.admin_usernames
        or normalized in extra_admins
        or is_runtime_admin(user_id)
    )


def admin_denied_text(message: Message) -> str:
    username = message.from_user.username or "нет username"
    return (
        "Доступ к админке пока не выдан.\n\n"
        f"Твой Telegram ID: <code>{message.from_user.id}</code>\n"
        f"Твой username: <code>@{username}</code>\n\n"
        "Если тебя добавили по username, проверь, что это именно username, а не имя профиля."
    )


def settings_text() -> str:
    s = all_settings()
    return (
        "⚙️ <b>Настройки бота</b>\n\n"
        f"📣 Канал: <code>{s.get('required_channel','')}</code>\n"
        f"🔗 Ссылка: <code>{s.get('required_channel_url','')}</code>\n"
        f"👤 Куратор: <code>{s.get('prize_contact','')}</code>\n"
        f"🤖 Бот: <code>@{s.get('bot_username','konkurs78bot').lstrip('@')}</code>\n"
        f"👑 Админы username: <code>{s.get('admin_usernames_extra','')}</code>\n"
        f"✅ Авто-победа: <code>{s.get('auto_win_enabled','1')}</code>\n"
        f"⏳ Через: <code>{s.get('auto_win_delay_seconds','')}</code> сек\n"
        f"🏆 Место: <code>{s.get('auto_win_place','1')}</code>\n"
        f"⏱ Задержка рассылки: <code>{s.get('broadcast_delay','')}</code> сек\n"
        f"👋 Premium 👋: <code>{s.get('custom_emoji_hello','')}</code>\n"
        f"🏆 Premium 🏆: <code>{s.get('custom_emoji_trophy','')}</code>\n"
        f"🎉 Premium 🎉: <code>{s.get('custom_emoji_party','')}</code>\n"
        f"✉️ Premium ✉️: <code>{s.get('custom_emoji_envelope','')}</code>\n"
        f"🥇 Premium 🥇: <code>{s.get('custom_emoji_medal','')}</code>\n\n"
        "Можно менять все тексты, кнопки, канал, контакт, задержки, админов и emoji.\n"
        "Шаблоны: {contact}, {first_name}, {channel}, {place}, {ref_link}, {bot_username}."
    )


@router.message(Command("admin"))
async def admin(message: Message):
    if not is_admin(message.from_user.id, message.from_user.username):
        await message.answer(admin_denied_text(message), parse_mode="HTML")
        return
    await message.answer("⚙️ Админ-панель", reply_markup=admin_keyboard())


@router.message(Command("id"))
async def my_id(message: Message):
    await message.answer(admin_denied_text(message), parse_mode="HTML")


@router.message(Command("admin_login"))
async def admin_login(message: Message):
    parts = (message.text or "").split(maxsplit=1)
    code = parts[1].strip() if len(parts) > 1 else ""
    if code and code == settings.admin_passcode:
        add_runtime_admin(message.from_user.id, message.from_user.username)
        await message.answer("✅ Доступ к админке выдан. Открываю панель.", reply_markup=admin_keyboard())
        return
    await message.answer("Команда входа: /admin_login КОД")


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id, callback.from_user.username):
        return
    await state.clear()
    await callback.message.answer("⚙️ Админ-панель", reply_markup=admin_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin_settings")
async def admin_settings(callback: CallbackQuery):
    if not is_admin(callback.from_user.id, callback.from_user.username):
        return
    await callback.message.answer(settings_text(), reply_markup=settings_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.in_(CALLBACK_TO_SETTING.keys()))
async def ask_setting(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id, callback.from_user.username):
        return
    key = CALLBACK_TO_SETTING[callback.data]
    await state.set_state(AdminState.waiting_setting_value)
    await state.update_data(setting_key=key)
    await callback.message.answer(
        f"Введи новое значение для: {SETTING_LABELS[key]}\n\n"
        "Примеры:\n"
        "Канал: @channel или -1001234567890\n"
        "Ссылка: https://t.me/channel\n"
        "Куратор: @admin\n"
        "Админы username: sexmakson,another_admin\n"
        "Авто-победа: 1 или 0\n"
        "Задержка: 0.05\n"
        "В текстах можно использовать {contact}, {first_name}, {channel}, {place}, {ref_link}, {bot_username}.",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(AdminState.waiting_setting_value)
async def save_setting(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id, message.from_user.username):
        return
    data = await state.get_data()
    key = data.get("setting_key")
    value = (message.text or "").strip()
    if key in {"broadcast_delay", "auto_win_delay_seconds"}:
        try:
            if float(value) < 0:
                raise ValueError
        except ValueError:
            await message.answer("Значение должно быть числом: например 0.05, 1 или 240")
            return
    set_setting(key, value)
    await state.clear()
    await message.answer(f"✅ Сохранено: {SETTING_LABELS.get(key, key)} = {value}")
    await message.answer(settings_text(), reply_markup=settings_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "admin_cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id, callback.from_user.username):
        return
    await state.clear()
    await callback.message.answer("Отменено.", reply_markup=admin_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id, callback.from_user.username):
        return
    s = stats()
    await callback.message.answer(f"📊 Статистика\nВсего: {s['total']}\nПодписаны: {s['subscribed']}\nПобедители: {s['winners']}")
    await callback.answer()


@router.callback_query(F.data == "admin_export")
async def admin_export(callback: CallbackQuery):
    if not is_admin(callback.from_user.id, callback.from_user.username):
        return
    path = export_csv(Path("participants.csv"))
    await callback.message.answer_document(FSInputFile(path), caption="📤 Участники CSV")
    await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
async def ask_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id, callback.from_user.username):
        return
    await state.set_state(AdminState.waiting_broadcast_text)
    default_text = all_settings().get("broadcast_win_text", "")
    await callback.message.answer(
        "✏️ Введи текст рассылки. Получат все подписанные участники.\n\n"
        f"Текущий шаблон:\n{default_text}",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(AdminState.waiting_broadcast_text)
async def run_broadcast(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id, message.from_user.username):
        return
    text = message.html_text
    await state.clear()
    asyncio.create_task(broadcast(bot, message.chat.id, text, only_subscribed=True))
    await message.answer("✅ Запустил рассылку в фоне. Бот остается доступным.", reply_markup=admin_keyboard())


@router.callback_query(F.data == "admin_winner")
async def ask_winner(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id, callback.from_user.username):
        return
    await state.set_state(AdminState.waiting_winner_id)
    await callback.message.answer("🏆 Пришли Telegram ID победителя, которого надо отметить и уведомить.", reply_markup=cancel_keyboard())
    await callback.answer()


@router.message(AdminState.waiting_winner_id)
async def mark_winner(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id, message.from_user.username):
        return
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("Нужен числовой Telegram ID.")
        return
    ok = set_winner(user_id, True)
    await state.clear()
    if not ok:
        await message.answer("Такого участника нет в базе.", reply_markup=admin_keyboard())
        return
    text = format_template("manual_winner_text")
    button_text = all_settings().get("winner_button_text", "забрать приз")
    await send_styled_message(user_id, text, inline_keyboard=[[styled_button(button_text, url=f"https://t.me/{prize_contact().lstrip('@')}", style="success")]])
    await message.answer(f"✅ Победитель {user_id} отмечен и уведомлен.", reply_markup=admin_keyboard())
