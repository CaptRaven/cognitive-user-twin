from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "Cognitive User Twin API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Engine Settings
    COGNITIVE_NOISE: float = 0.05
    NIGERIAN_REALISM: bool = True
    
    # AI Settings
    MISTRAL_API_KEY: str = ""
    MISTRAL_MODEL: str = "mistral-tiny"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
