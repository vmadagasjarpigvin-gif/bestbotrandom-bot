import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _ids(value: str) -> set[int]:
    out: set[int] = set()
    for part in (value or "").split(","):
        part = part.strip()
        if part:
            out.add(int(part))
    return out


def _usernames(value: str) -> set[str]:
    out: set[str] = set()
    for part in (value or "").split(","):
        part = part.strip().lower().lstrip("@")
        if part:
            out.add(part)
    return out


@dataclass(frozen=True)
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    admin_ids: set[int] = None
    admin_usernames: set[str] = None
    required_channel: str = os.getenv("REQUIRED_CHANNEL", "")
    required_channel_url: str = os.getenv("REQUIRED_CHANNEL_URL", "")
    prize_contact: str = os.getenv("PRIZE_CONTACT", "@admin")
    db_path: str = os.getenv("DB_PATH", "bot.sqlite3")
    broadcast_delay: float = float(os.getenv("BROADCAST_DELAY", "0.05"))
    custom_emoji_gift: str = os.getenv("CUSTOM_EMOJI_GIFT", "")
    custom_emoji_bell: str = os.getenv("CUSTOM_EMOJI_BELL", "")
    custom_emoji_lock: str = os.getenv("CUSTOM_EMOJI_LOCK", "")
    admin_passcode: str = os.getenv("ADMIN_PASSCODE", "admin181608")

    def __post_init__(self):
        object.__setattr__(self, "admin_ids", _ids(os.getenv("ADMIN_IDS", "")))
        object.__setattr__(self, "admin_usernames", _usernames(os.getenv("ADMIN_USERNAMES", "")))
        if not self.bot_token:
            raise RuntimeError("Set BOT_TOKEN in .env")


settings = Settings()
