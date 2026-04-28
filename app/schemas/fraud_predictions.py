from pydantic import BaseModel
from typing import Optional


class FraudTransactionInput(BaseModel):
    amount: float
    transaction_type: Optional[str] = None
    hour: Optional[int] = None
    is_weekend: Optional[int] = None
    is_night: Optional[int] = None
    velocity_score: Optional[float] = 0.0
    geo_anomaly_score: Optional[float] = 0.0
    spending_deviation_score: Optional[float] = 0.0


class FraudPredictionOutput(BaseModel):
    fraud_score: float
    is_fraud: bool
    confidence: str  # "low" | "medium" | "high"
    action: str      # "block" | "flag" | "allow"
