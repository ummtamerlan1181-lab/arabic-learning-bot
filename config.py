import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DB_PATH: str = os.getenv("DB_PATH", "arabic_bot.db")

    def validate(self) -> None:
        missing = [k for k in ("BOT_TOKEN", "GEMINI_API_KEY") if not getattr(self, k)]
        if missing:
            raise ValueError(f"Missing required env vars: {', '.join(missing)}")


config = Config()
config.validate()
