from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_settings")],
        [InlineKeyboardButton(text="📤 Экспорт CSV", callback_data="admin_export")],
        [InlineKeyboardButton(text="🔔 Рассылка всем", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🏆 Отметить победителя", callback_data="admin_winner")],
    ])


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📣 Канал", callback_data="set_required_channel"), InlineKeyboardButton(text="🔗 Ссылка", callback_data="set_required_channel_url")],
        [InlineKeyboardButton(text="👤 Куратор", callback_data="set_prize_contact"), InlineKeyboardButton(text="🤖 Username бота", callback_data="set_bot_username")],
        [InlineKeyboardButton(text="🏆 Место", callback_data="set_auto_win_place")],
        [InlineKeyboardButton(text="✅ Авто-победа вкл/выкл", callback_data="set_auto_win_enabled")],
        [InlineKeyboardButton(text="⏳ Время до авто-победы", callback_data="set_auto_win_delay_seconds")],
        [InlineKeyboardButton(text="👋 Приветствие", callback_data="set_welcome_text")],
        [InlineKeyboardButton(text="🎉 Кнопка участия", callback_data="set_join_button_text")],
        [InlineKeyboardButton(text="📣 Текст подписки", callback_data="set_subscribe_text")],
        [InlineKeyboardButton(text="📣 Кнопка подписки", callback_data="set_subscribe_button_text")],
        [InlineKeyboardButton(text="✅ Кнопка проверки", callback_data="set_check_button_text")],
        [InlineKeyboardButton(text="🔒 Текст нет подписки", callback_data="set_not_subscribed_text")],
        [InlineKeyboardButton(text="🎊 Текст регистрации", callback_data="set_registered_text")],
        [InlineKeyboardButton(text="🏆 Текст авто-победы", callback_data="set_auto_win_text")],
        [InlineKeyboardButton(text="🏆 Текст ручного победителя", callback_data="set_manual_winner_text")],
        [InlineKeyboardButton(text="🔘 Кнопка победителя", callback_data="set_winner_button_text")],
        [InlineKeyboardButton(text="📨 Текст рассылки", callback_data="set_broadcast_win_text")],
        [InlineKeyboardButton(text="⏱ Задержка рассылки", callback_data="set_broadcast_delay")],
        [InlineKeyboardButton(text="👋 Premium 👋", callback_data="set_custom_emoji_hello")],
        [InlineKeyboardButton(text="🏆 Premium 🏆", callback_data="set_custom_emoji_trophy"), InlineKeyboardButton(text="🎉 Premium 🎉", callback_data="set_custom_emoji_party")],
        [InlineKeyboardButton(text="✉️ Premium ✉️", callback_data="set_custom_emoji_envelope"), InlineKeyboardButton(text="🥇 Premium 🥇", callback_data="set_custom_emoji_medal")],
        [InlineKeyboardButton(text="🎁 Emoji gift", callback_data="set_custom_emoji_gift"), InlineKeyboardButton(text="🔔 Emoji bell", callback_data="set_custom_emoji_bell")],
        [InlineKeyboardButton(text="🔒 Emoji lock", callback_data="set_custom_emoji_lock")],
        [InlineKeyboardButton(text="👑 Username админа", callback_data="set_admin_usernames_extra")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")],
    ])


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")]])
