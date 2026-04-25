import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bunker.db")
    webhook_url: str = os.getenv("WEBHOOK_URL", "")
    webhook_secret: str = os.getenv("WEBHOOK_SECRET", "")
    port: int = int(os.getenv("PORT", "8080"))
    admin_user_ids: tuple[int, ...] = tuple(
        int(x.strip()) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip().isdigit()
    )
    join_timeout: int = int(os.getenv("JOIN_TIMEOUT", "180"))
    discussion_timeout: int = int(os.getenv("DISCUSSION_TIMEOUT", "180"))
    voting_timeout: int = int(os.getenv("VOTING_TIMEOUT", "60"))
    presentation_timeout: int = int(os.getenv("PRESENTATION_TIMEOUT", "120"))
    reminder_interval: int = int(os.getenv("REMINDER_INTERVAL", "30"))
    min_players: int = int(os.getenv("MIN_PLAYERS", "4"))
    max_players: int = int(os.getenv("MAX_PLAYERS", "10"))


settings = Settings()
