"""
Schémas Pydantic pour les prédictions
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class PurchaseHistoryItem(BaseModel):
    """Item d'historique d'achat"""
    date: str = Field(..., description="Date de l'achat (YYYY-MM-DD)")
    product_id: str = Field(..., description="ID du produit")
    product_name: str = Field(..., description="Nom du produit")
    quantity: float = Field(..., gt=0, description="Quantité commandée")
    price: float = Field(..., ge=0, description="Prix unitaire HT")
    supplier: Optional[str] = Field(None, description="Nom du fournisseur")
    category: Optional[str] = Field(None, description="Catégorie du produit")
    
    @validator('date')
    def validate_date(cls, v):
        """Valider le format de la date"""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Format de date invalide. Utilisez YYYY-MM-DD')


class PredictionRequest(BaseModel):
    """Requête de prédiction pour un produit"""
    product_id: str = Field(..., description="ID du produit")
    history: List[PurchaseHistoryItem] = Field(..., min_items=1, description="Historique des achats")
    prediction_days: int = Field(30, ge=1, le=365, description="Horizon de prédiction en jours")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod-123",
                "history": [
                    {
                        "date": "2024-01-15",
                        "product_id": "prod-123",
                        "product_name": "Papier A4",
                        "quantity": 50.0,
                        "price": 25.5,
                        "supplier": "Fournisseur A",
                        "category": "Fournitures"
                    }
                ],
                "prediction_days": 30
            }
        }


class PredictionResponse(BaseModel):
    """Réponse de prédiction"""
    product_id: str
    product_name: str
    predicted_quantity: float = Field(..., description="Quantité prédite à commander")
    predicted_date: str = Field(..., description="Date prédite de commande")
    confidence: float = Field(..., ge=0, le=1, description="Score de confiance (0-1)")
    recommendation: str = Field(..., description="Recommandation textuelle")
    historical_avg: float = Field(..., description="Moyenne historique des quantités")
    trend: str = Field(..., description="Tendance: increasing, stable, decreasing")
    days_until_order: int = Field(..., description="Jours avant la commande recommandée")
    estimated_value: Optional[float] = Field(None, description="Valeur estimée de la commande")
    urgency_level: str = Field(..., description="Niveau d'urgence: urgent, soon, planned")
    
    # Métriques additionnelles
    data_quality: Dict[str, Any] = Field(default_factory=dict, description="Qualité des données")
    seasonality_detected: bool = Field(False, description="Saisonnalité détectée")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod-123",
                "product_name": "Papier A4",
                "predicted_quantity": 45.5,
                "predicted_date": "2024-02-15",
                "confidence": 0.87,
                "recommendation": "🟠 BIENTÔT - Commander 46 unités d'ici 15 jours. Haute confiance. ➡️ Demande stable.",
                "historical_avg": 48.3,
                "trend": "stable",
                "days_until_order": 15,
                "estimated_value": 1161.75,
                "urgency_level": "soon",
                "data_quality": {
                    "data_points": 12,
                    "regularity_score": 0.85,
                    "stability_score": 0.92
                },
                "seasonality_detected": False
            }
        }


class ProductPredictionRequest(BaseModel):
    """Requête pour un produit dans un batch"""
    product_id: str
    history: List[PurchaseHistoryItem]


class BatchPredictionRequest(BaseModel):
    """Requête de prédiction en batch"""
    products: List[ProductPredictionRequest] = Field(..., min_items=1, description="Liste des produits")
    prediction_days: int = Field(30, ge=1, le=365, description="Horizon de prédiction")
    
    class Config:
        json_schema_extra = {
            "example": {
                "products": [
                    {
                        "product_id": "prod-123",
                        "history": [
                            {
                                "date": "2024-01-15",
                                "product_id": "prod-123",
                                "product_name": "Papier A4",
                                "quantity": 50.0,
                                "price": 25.5
                            }
                        ]
                    }
                ],
                "prediction_days": 30
            }
        }


class BatchPredictionResponse(BaseModel):
    """Réponse de prédiction en batch"""
    predictions: List[PredictionResponse]
    errors: List[Dict[str, str]] = Field(default_factory=list)
    total_processed: int
    successful: int
    failed: int


class RecommendationsResponse(BaseModel):
    """Réponse avec les recommandations d'achat"""
    recommendations: List[PredictionResponse]
    total_recommendations: int
    urgent_count: int = Field(..., description="Nombre de commandes urgentes (< 7 jours)")
    total_estimated_value: float = Field(..., description="Valeur totale estimée des commandes")
    generated_at: str = Field(..., description="Timestamp de génération")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommendations": [],
                "total_recommendations": 5,
                "urgent_count": 2,
                "total_estimated_value": 15420.50,
                "generated_at": "2024-01-31T10:30:00Z"
            }
        }
