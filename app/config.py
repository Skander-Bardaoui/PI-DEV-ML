"""
Configuration du service ML
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/pi_dev"
    
    # ML Configuration
    ML_MODEL_PATH: str = "./app/models/trained_models"
    MIN_DATA_POINTS: int = 5
    CONFIDENCE_THRESHOLD: float = 0.6
    PREDICTION_HORIZON_DAYS: int = 30
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "ML Purchase Prediction Service"
    VERSION: str = "1.0.0"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3001",
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/ml-service.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
