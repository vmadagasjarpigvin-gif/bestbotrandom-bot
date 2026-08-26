from app.raw_api import styled_button
from app.services.settings_store import required_channel_url, prize_contact, required_channel, get_setting, format_template


def start_keyboard() -> dict:
    return {"inline_keyboard": [[styled_button(get_setting("join_button_text", "🎉 Участвовать в конкурсе"), callback_data="join_contest", style="primary")]]}


def subscribe_keyboard() -> dict:
    channel = required_channel().lstrip("@") or "канал"
    sub_text = format_template("subscribe_button_text", channel="@" + channel)
    check_text = get_setting("check_button_text", "✅ Я подписался — проверить")
    return {
        "inline_keyboard": [
            [styled_button(sub_text, url=required_channel_url(), style="primary")],
            [styled_button(check_text, callback_data="check_sub", style="success")],
        ]
    }


def contact_keyboard(label_key: str = "contact_button_text") -> list[list[dict]]:
    return [[styled_button(get_setting(label_key, "связаться"), url=f"https://t.me/{prize_contact().lstrip('@')}", style="primary")]]
