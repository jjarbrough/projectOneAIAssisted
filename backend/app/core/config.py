from dataclasses import dataclass
import os
from functools import lru_cache


@dataclass(slots=True)
class Settings:
    app_name: str = "TaskTrack"
    database_url: str = "sqlite:///./tasktrack.db"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"


@lru_cache
def get_settings() -> Settings:
    defaults = Settings()
    return Settings(
        app_name=os.getenv("APP_NAME", defaults.app_name),
        database_url=os.getenv("DATABASE_URL", defaults.database_url),
        secret_key=os.getenv("SECRET_KEY", defaults.secret_key),
        access_token_expire_minutes=int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", defaults.access_token_expire_minutes)
        ),
        algorithm=os.getenv("AUTH_ALGORITHM", defaults.algorithm),
    )

