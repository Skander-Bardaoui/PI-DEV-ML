"""
Schémas Pydantic pour les prédictions de ventes
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class SalesHistoryItem(BaseModel):
    """Item d'historique de ventes"""
    date: str = Field(..., description="Date de la vente (YYYY-MM-DD)")
    amount: float = Field(..., gt=0, description="Montant de la vente")
    quantity: Optional[int] = Field(None, description="Quantité vendue")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-15",
                "amount": 1250.50,
                "quantity": 5
            }
        }


class SalesForecastRequest(BaseModel):
    """Requête de prédiction de ventes"""
    sales_history: List[SalesHistoryItem] = Field(..., min_length=3, description="Historique des ventes (min 3 entrées)")
    forecast_days: int = Field(30, gt=0, le=365, description="Nombre de jours à prédire")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sales_history": [
                    {"date": "2024-01-01", "amount": 1000.0, "quantity": 10},
                    {"date": "2024-01-02", "amount": 1500.0, "quantity": 15},
                    {"date": "2024-01-03", "amount": 1200.0, "quantity": 12}
                ],
                "forecast_days": 30
            }
        }


class SalesForecastResponse(BaseModel):
    """Réponse de prédiction de ventes"""
    forecast_days: int
    predicted_sales: float
    predicted_daily_avg: float
    current_daily_avg: float
    trend: str
    confidence: float
    best_selling_days: List[str]
    seasonality_detected: bool
    growth_rate: float
    recommendation: str


class ClientPurchaseItem(BaseModel):
    """Item d'achat client"""
    date: str
    amount: float
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None


class ClientChurnRequest(BaseModel):
    """Requête de prédiction de churn client"""
    client_id: str
    client_history: List[ClientPurchaseItem] = Field(..., min_length=2)
    
    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "client-123",
                "client_history": [
                    {
                        "date": "2024-01-01",
                        "amount": 500.0,
                        "product_id": "prod-1",
                        "product_name": "Product A",
                        "category": "Electronics",
                        "price": 500.0
                    }
                ]
            }
        }


class ClientChurnResponse(BaseModel):
    """Réponse de prédiction de churn"""
    client_id: str
    churn_risk_score: float
    risk_level: str
    days_since_last_purchase: int
    average_purchase_interval: float
    purchase_frequency_per_month: float
    recommendation: str


class Product(BaseModel):
    """Produit pour recommandations"""
    id: str
    name: str
    price: float
    category: Optional[str] = None
    popularity: Optional[float] = None


class ProductRecommendationRequest(BaseModel):
    """Requête de recommandation de produits"""
    client_id: str
    client_purchases: List[ClientPurchaseItem]
    available_products: List[Product]
    
    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "client-123",
                "client_purchases": [
                    {
                        "date": "2024-01-01",
                        "amount": 500.0,
                        "product_id": "prod-1",
                        "category": "Electronics",
                        "price": 500.0
                    }
                ],
                "available_products": [
                    {
                        "id": "prod-2",
                        "name": "Product B",
                        "price": 450.0,
                        "category": "Electronics",
                        "popularity": 0.8
                    }
                ]
            }
        }


class ProductRecommendation(BaseModel):
    """Recommandation de produit"""
    product_id: str
    product_name: str
    score: float
    reason: str


class ProductRecommendationResponse(BaseModel):
    """Réponse de recommandation de produits"""
    client_id: str
    recommendations: List[ProductRecommendation]
    total_recommendations: int
