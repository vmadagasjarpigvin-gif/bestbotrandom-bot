import re
import aiohttp
from .config import settings

API_BASE = "https://api.telegram.org/bot{token}/{method}"

TG_EMOJI_RE = re.compile(r'<tg-emoji\s+emoji-id=["\'](\d+)["\']>(.*?)</tg-emoji>', re.S)
BOLD_RE = re.compile(r'<b>(.*?)</b>', re.S)
TAG_RE = re.compile(r'<tg-emoji\s+emoji-id=["\'](\d+)["\']>(.*?)</tg-emoji>|<b>(.*?)</b>', re.S)


def utf16_len(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def parse_entities(html: str) -> tuple[str, list[dict]]:
    """Convert our simple HTML subset to Bot API MessageEntity objects.

    Telegram sometimes renders <tg-emoji> in button/message text as fallback.
    Explicit custom_emoji entities force premium emoji rendering in messages.
    Supported tags: <tg-emoji emoji-id="...">X</tg-emoji> and <b>text</b>.
    """
    out = []
    entities = []
    last = 0
    for m in TAG_RE.finditer(html):
        before = html[last:m.start()]
        out.append(before)
        offset = utf16_len("".join(out))
        if m.group(1):
            emoji_id = m.group(1)
            body = m.group(2)
            out.append(body)
            entities.append({
                "type": "custom_emoji",
                "offset": offset,
                "length": utf16_len(body),
                "custom_emoji_id": emoji_id,
            })
        else:
            body = m.group(3)
            out.append(body)
            entities.append({"type": "bold", "offset": offset, "length": utf16_len(body)})
        last = m.end()
    out.append(html[last:])
    text = "".join(out)
    return text, entities


def styled_button(text: str, callback_data: str | None = None, url: str | None = None,
                  style: str | None = None, icon_custom_emoji_id: str | None = None) -> dict:
    btn = {"text": text}
    if callback_data:
        btn["callback_data"] = callback_data
    if url:
        btn["url"] = url
    if style:
        btn["style"] = style
    if icon_custom_emoji_id:
        btn["icon_custom_emoji_id"] = icon_custom_emoji_id
    return btn


async def api_call(method: str, payload: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(API_BASE.format(token=settings.bot_token, method=method), json=payload) as resp:
            data = await resp.json(content_type=None)
            if not data.get("ok"):
                raise RuntimeError(f"Telegram API {method} failed: {data}")
            return data


async def send_styled_message(chat_id: int, text: str, inline_keyboard: list[list[dict]] | None = None,
                              parse_mode: str = "HTML") -> dict:
    payload = {"chat_id": chat_id}
    # For premium emoji, send explicit MessageEntity objects instead of relying on parse_mode.
    if "<tg-emoji" in text:
        plain_text, entities = parse_entities(text)
        payload["text"] = plain_text
        payload["entities"] = entities
    else:
        payload["text"] = text
        payload["parse_mode"] = parse_mode
    if inline_keyboard:
        payload["reply_markup"] = {"inline_keyboard": inline_keyboard}
    return await api_call("sendMessage", payload)
