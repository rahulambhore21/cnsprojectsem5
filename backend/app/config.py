import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "ULPF — Universal Log Pre-processing Framework"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Database
    MONGODB_URI: str = Field(default="mongodb://localhost:27017")
    DATABASE_NAME: str = Field(default="ulpf")
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000"
    
    # Security / limits
    API_KEY: str = Field(default="", description="If set, all /api routes except /api/health require header X-API-Key")
    MAX_UPLOAD_BYTES: int = 5 * 1024 * 1024
    MAX_UPLOAD_LINES: int = 500
    MAX_BATCH_LOGS: int = 500
    MAX_REGEX_LENGTH: int = 500

    # OpenAI
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
