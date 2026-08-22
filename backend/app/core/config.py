from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "satquery-backend"
    API_V1_STR: str = "/api/v1"
    
    # CORS Origins allowed to access the API. Defaults to common frontend development ports.
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
