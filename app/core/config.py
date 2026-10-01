import os
from typing import Set
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Beauty Studio API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days


    # OpenAI / AI Provider settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_IMAGE_MODEL: str = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2.5-flare")
    OPENAI_IMAGE_QUALITY: str = os.getenv("OPENAI_IMAGE_QUALITY", "medium")
    OPENAI_INPUT_FIDELITY: str = os.getenv("OPENAI_INPUT_FIDELITY", "")
    CUSTOM_IMAGE_COST_USD: str = os.getenv("CUSTOM_IMAGE_COST_USD", "")
    INPUT_TOKEN_RATE_PER_M: float = float(os.getenv("INPUT_TOKEN_RATE_PER_M", "8.00"))
    OUTPUT_TOKEN_RATE_PER_M: float = float(os.getenv("OUTPUT_TOKEN_RATE_PER_M", "30.00"))

    # Image validation parameters
    MAX_BYTES: int = 12 * 1024 * 1024  # 12 MB
    MIN_SIDE: int = int(os.getenv("MIN_IMAGE_SIDE", "256"))
    MAX_SIDE: int = 1536
    ALLOWED_FORMATS: Set[str] = {"JPEG", "PNG", "WEBP"}
    CATEGORIES: Set[str] = {"Hairstyle", "Makeup", "Nail art", "Overall beauty look"}

    # Database & Storage
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ai_beauty_studio.db")
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")  # "local" or "s3"
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "ai-beauty-studio-assets")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")

    # Rate Limiting & Quotas
    RATE_LIMIT_PER_DAY: int = int(os.getenv("RATE_LIMIT_PER_DAY", "10"))

    model_config = {"case_sensitive": True, "env_file": ".env", "extra": "ignore"}




settings = Settings()

