from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    APP_NAME: str = "Cognitive User Twin API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = "0.0.0.0"
    
    # Engine Settings
    COGNITIVE_NOISE: float = 0.05
    NIGERIAN_REALISM: bool = True
    
    # AI Settings
    MISTRAL_API_KEY: str = ""
    MISTRAL_MODEL: str = "mistral-tiny"
    
    # Extra fields from error
    environment: str = "production"
    chroma_dir: str = "data/chroma"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
