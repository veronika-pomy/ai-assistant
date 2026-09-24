import os
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings loaded from environment variables."""
    model_name: str
    default_model_name: str
    how_many_searches: int
    session_type: str
    session_name: str

    @classmethod
    def load(cls):
        """Load settings from environment variables with defaults."""
        load_dotenv(override=True)
        return cls(
            model_name=os.getenv("MODEL_NAME", "gpt-5.4-mini"),
            default_model_name=os.getenv("DEFAULT_MODEL_NAME", "gpt-5.4-mini"),
            how_many_searches=int(os.getenv("HOW_MANY_SEARCHES", "5")),
            session_type=os.getenv("SESSION_TYPE", "memory"),
            session_name=os.getenv("SESSION_NAME", "nelle")
        )


def get_settings() -> Settings:
    """Get application settings."""
    return Settings.load()
