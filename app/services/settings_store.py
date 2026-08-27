from app.config import settings as env_settings
from app.db import conn

DEFAULTS = {
    'required_channel': env_settings.required_channel,
    'required_channel_url': env_settings.required_channel_url,
    'prize_contact': env_settings.prize_contact,
    'broadcast_delay': str(env_settings.broadcast_delay),
    'custom_emoji_gift': env_settings.custom_emoji_gift,
    'custom_emoji_bell': env_settings.custom_emoji_bell,
    'custom_emoji_lock': env_settings.custom_emoji_lock,
    'custom_emoji_hello': '5237763160647149111',
    'custom_emoji_trophy': '5440539497383087970',
    'custom_emoji_party': '5253742260054409879',
    'custom_emoji_envelope': '5461151367559141950',
    'custom_emoji_medal': '5386750400709819565',
    'bot_username': 'bestbotrandom_bot',
    'giveaway_title': 'Конкурс',
    'join_button_text': '🎉 Участвовать в конкурсе',
    'contact_button_text': 'связаться',
    'claim_button_text': 'забрать приз',
    'winner_button_text': 'забрать приз',
    'subscribe_button_text': '📣 Подписаться на {channel}',
    'check_button_text': '✅ Я подписался — проверить',
    'auto_win_enabled': '0',
    'auto_win_delay_seconds': '240',
    'auto_win_place': '1',
    'welcome_text': '<tg-emoji emoji-id="5237763160647149111">👋</tg-emoji> Привет, {first_name}!\\n\\n<tg-emoji emoji-id="5253742260054409879">🎉</tg-emoji> Добро пожаловать в Конкурс!\\n\\nНажми кнопку ниже, чтобы участвовать.',
    'subscribe_text': '📣 <b>Для участия нужно подписаться на канал!</b>\n\n1️⃣ Нажми кнопку ниже и подпишись\n2️⃣ Вернись и нажми «✅ Я подписался — проверить»',
    'not_subscribed_text': '🔒 Подписка пока не найдена. Подпишись на канал и нажми проверку еще раз.',
    'registered_text': '<tg-emoji emoji-id="5253742260054409879">🎉</tg-emoji> <b>Ты успешно зарегистрирован!</b>\n\nТы в списке участников конкурса.\nОжидай результатов — мы обязательно напишем тебе! ☘️\n\n🔗 <b>Твоя ссылка для друзей:</b>\n{ref_link}\nКаждый друг, который придет по ней и станет участником, даёт тебе <b>+1 шанс.</b>',
    'auto_win_text': '<tg-emoji emoji-id="5440539497383087970">🏆</tg-emoji> <b>Поздравляем! Подведены итоги конкурса!</b>\n\n<tg-emoji emoji-id="5386750400709819565">🥇</tg-emoji> Ты занял(а) {place} место!\n\n<tg-emoji emoji-id="5461151367559141950">✉️</tg-emoji> Для получения приза напиши куратору: {contact}\n\nПоздравляем с победой! <tg-emoji emoji-id="5253742260054409879">🎉</tg-emoji>',
    'manual_winner_text': '<tg-emoji emoji-id="5440539497383087970">🏆</tg-emoji> <b>Поздравляем! Подведены итоги конкурса!</b>\n\n<tg-emoji emoji-id="5386750400709819565">🥇</tg-emoji> Ты занял(а) {place} место!\n\n<tg-emoji emoji-id="5461151367559141950">✉️</tg-emoji> Для получения приза напиши куратору: {contact}\n\nПоздравляем с победой! <tg-emoji emoji-id="5253742260054409879">🎉</tg-emoji>',
    'broadcast_win_text': 'Уважаемое 2-е место, выйдем на связь?\nУже всем выдала, остался только ты, отпиши мне {contact} выдам ваш приз Telegram Premium на год или 3000₽',
}


def init_settings() -> None:
    with conn() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS settings(
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        for key, value in DEFAULTS.items():
            db.execute("INSERT OR IGNORE INTO settings(key, value) VALUES(?, ?)", (key, value or ""))


def get_setting(key: str, default: str = "") -> str:
    with conn() as db:
        row = db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    with conn() as db:
        db.execute("INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value or ""))


def all_settings() -> dict[str, str]:
    init_settings()
    with conn() as db:
        return {row["key"]: row["value"] for row in db.execute("SELECT key, value FROM settings ORDER BY key")}


def required_channel() -> str:
    return get_setting("required_channel", env_settings.required_channel)


def required_channel_url() -> str:
    return get_setting("required_channel_url", env_settings.required_channel_url)


def prize_contact() -> str:
    return get_setting("prize_contact", env_settings.prize_contact)


def broadcast_delay() -> float:
    try:
        return float(get_setting("broadcast_delay", str(env_settings.broadcast_delay)))
    except ValueError:
        return env_settings.broadcast_delay


def auto_win_delay() -> float:
    try:
        return max(0.0, float(get_setting("auto_win_delay_seconds", "240")))
    except ValueError:
        return 240.0


def auto_win_enabled() -> bool:
    return get_setting("auto_win_enabled", "1").strip().lower() in {"1", "true", "yes", "on", "да", "вкл"}


def format_template(key: str, **extra: str) -> str:
    bot_username = get_setting("bot_username", "bestbotrandom_bot").lstrip("@")
    user_id = extra.get("user_id", "")
    values = {
        "contact": prize_contact(),
        "channel": required_channel(),
        "place": get_setting("auto_win_place", "1"),
        "bot_username": bot_username,
        "ref_link": f"https://t.me/{bot_username}?start=ref{user_id}" if user_id else f"https://t.me/{bot_username}",
        **extra,
    }
    text = get_setting(key, DEFAULTS.get(key, ""))
    for k, v in values.items():
        text = text.replace("{" + k + "}", str(v))
    return text
