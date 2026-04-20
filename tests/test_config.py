"""
Tests pour la configuration
"""
import pytest
from app.config import Settings


class TestSettings:
    """Tests de la classe Settings"""
    
    def test_default_settings(self):
        """Test des valeurs par défaut"""
        settings = Settings()
        
        assert settings.PROJECT_NAME == "ML Purchase Prediction Service"
        assert settings.VERSION == "1.0.0"
        assert settings.API_V1_PREFIX == "/api/v1"
        assert settings.MIN_DATA_POINTS == 5
        assert settings.CONFIDENCE_THRESHOLD == 0.6
        assert settings.PREDICTION_HORIZON_DAYS == 30
    
    def test_log_level(self):
        """Test du niveau de log"""
        settings = Settings()
        assert settings.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR"]
    
    def test_cors_origins(self):
        """Test des origines CORS"""
        settings = Settings()
        assert isinstance(settings.CORS_ORIGINS, list)
        assert len(settings.CORS_ORIGINS) > 0
    
    def test_database_url_format(self):
        """Test du format de l'URL de base de données"""
        settings = Settings()
        assert settings.DATABASE_URL.startswith("postgresql://")
    
    def test_ml_model_path(self):
        """Test du chemin des modèles ML"""
        settings = Settings()
        assert settings.ML_MODEL_PATH is not None
        assert len(settings.ML_MODEL_PATH) > 0
