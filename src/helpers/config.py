from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Point to src/ folder
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str
    
    FILE_ALLOWED_TYPES : list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    MONGODB_URL: str
    MONGODB_DATABASE: str

def get_settings():
    return Settings()