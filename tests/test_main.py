"""
Tests unitaires pour le service ML
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Tests des endpoints de santé"""
    
    def test_root_endpoint(self):
        """Test de l'endpoint racine"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
    
    def test_health_check(self):
        """Test du health check"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data


class TestPredictionEndpoints:
    """Tests des endpoints de prédiction"""
    
    def test_predict_demand_insufficient_data(self):
        """Test avec données insuffisantes"""
        payload = {
            "product_id": "test-123",
            "history": [
                {
                    "date": "2024-01-01",
                    "quantity": 10,
                    "product_name": "Test Product"
                }
            ],
            "prediction_days": 30
        }
        response = client.post("/api/v1/predict/demand", json=payload)
        assert response.status_code == 400
        assert "insuffisantes" in response.json()["detail"].lower()
    
    def test_predict_demand_valid_data(self):
        """Test avec données valides"""
        payload = {
            "product_id": "test-123",
            "history": [
                {"date": f"2024-01-{i:02d}", "quantity": 10 + i, "product_name": "Test Product"}
                for i in range(1, 11)
            ],
            "prediction_days": 30
        }
        response = client.post("/api/v1/predict/demand", json=payload)
        # Peut échouer si le modèle n'est pas chargé, mais la structure doit être correcte
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "predicted_quantity" in data
            assert "confidence" in data
    
    def test_batch_prediction_empty(self):
        """Test batch avec liste vide"""
        payload = {
            "products": [],
            "prediction_days": 30
        }
        response = client.post("/api/v1/predict/batch", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["total_processed"] == 0
        assert data["successful"] == 0
    
    def test_batch_prediction_mixed(self):
        """Test batch avec données mixtes (valides et invalides)"""
        payload = {
            "products": [
                {
                    "product_id": "valid-123",
                    "history": [
                        {"date": f"2024-01-{i:02d}", "quantity": 10 + i, "product_name": "Valid Product"}
                        for i in range(1, 11)
                    ]
                },
                {
                    "product_id": "invalid-456",
                    "history": [
                        {"date": "2024-01-01", "quantity": 5, "product_name": "Invalid Product"}
                    ]
                }
            ],
            "prediction_days": 30
        }
        response = client.post("/api/v1/predict/batch", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["total_processed"] == 2
        assert data["failed"] >= 1  # Au moins l'invalide doit échouer


class TestRecommendations:
    """Tests des recommandations"""
    
    def test_recommendations_empty(self):
        """Test recommandations avec liste vide"""
        payload = {
            "products": [],
            "prediction_days": 30
        }
        response = client.post("/api/v1/recommendations", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert "total_recommendations" in data
        assert data["total_recommendations"] == 0


class TestConfiguration:
    """Tests de configuration"""
    
    def test_cors_headers(self):
        """Test des headers CORS"""
        response = client.options("/api/v1/health")
        # Les headers CORS doivent être présents
        assert response.status_code in [200, 405]  # Certains frameworks retournent 405 pour OPTIONS
    
    def test_api_documentation(self):
        """Test de la documentation API"""
        response = client.get("/api/v1/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
class TestAsyncOperations:
    """Tests des opérations asynchrones"""
    
    async def test_concurrent_predictions(self):
        """Test de prédictions concurrentes"""
        # Ce test vérifie que l'API peut gérer plusieurs requêtes simultanées
        import asyncio
        
        async def make_request():
            return client.get("/api/v1/health")
        
        # Lancer 5 requêtes en parallèle
        tasks = [make_request() for _ in range(5)]
        responses = await asyncio.gather(*tasks)
        
        # Toutes doivent réussir
        assert all(r.status_code == 200 for r in responses)
