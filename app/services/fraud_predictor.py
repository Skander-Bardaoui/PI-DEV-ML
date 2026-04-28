import numpy as np
import httpx
import os
from loguru import logger
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from typing import Dict, Any, List


class FraudPredictor:
    """
    Fraud detector that trains on real transaction data from the NestJS backend.
    Falls back to synthetic data if not enough real labeled data exists yet.
    Uses the same pipeline as the fraud_detection_notebook:
    SMOTE + StandardScaler + RandomForestClassifier
    """

    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1,
        )
        self.scaler = StandardScaler()
        self.model_trained = False
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:3000")

    # ------------------------------------------------------------------
    # Fetch real labeled data from NestJS backend
    # ------------------------------------------------------------------
    def _fetch_real_data(self):
        """
        Calls GET /transactions/training-data on the NestJS backend.
        Returns (X, y) numpy arrays or (None, None) if not enough data.
        """
        try:
            url = f"{self.backend_url}/transactions/training-data"
            response = httpx.get(url, timeout=10)
            response.raise_for_status()
            records: List[Dict] = response.json()

            if len(records) < 20:
                logger.warning(
                    f"⚠️ Only {len(records)} labeled transactions in DB "
                    f"— need at least 20. Using synthetic data."
                )
                return None, None

            X = np.array([[
                r["amount"],
                r["hour"],
                r["is_weekend"],
                r["is_night"],
                r["velocity_score"],
                r["geo_anomaly_score"],
                r["spending_deviation_score"],
            ] for r in records])

            y = np.array([r["is_fraud"] for r in records])

            n_fraud = int(y.sum())
            n_legit = len(y) - n_fraud
            logger.info(
                f"📊 Real data loaded: {len(records)} transactions "
                f"({n_fraud} fraud, {n_legit} legitimate)"
            )
            return X, y

        except Exception as e:
            logger.warning(f"⚠️ Could not fetch real data from backend: {e}")
            return None, None

    # ------------------------------------------------------------------
    # Synthetic fallback — only used when no real data is available yet
    # ------------------------------------------------------------------
    def _get_synthetic_data(self):
        """
        Synthetic training data that mirrors the notebook feature set.
        Used only until enough real labeled transactions exist in the DB.
        """
        logger.info("🔄 Using synthetic training data (no real data yet)")
        np.random.seed(42)
        n_legit = 800
        n_fraud = 200

        # Legitimate transactions — low amounts, business hours, low risk scores
        legit = np.column_stack([
            np.random.uniform(10, 3000, n_legit),       # amount
            np.random.randint(8, 20, n_legit),           # hour (business hours)
            np.random.randint(0, 2, n_legit),            # is_weekend
            np.zeros(n_legit),                           # is_night
            np.random.uniform(0, 0.3, n_legit),          # velocity_score
            np.random.uniform(0, 0.3, n_legit),          # geo_anomaly_score
            np.random.uniform(0, 0.3, n_legit),          # spending_deviation_score
        ])

        # Fraudulent transactions — high amounts, night hours, high risk scores
        fraud = np.column_stack([
            np.random.uniform(2000, 15000, n_fraud),
            np.random.choice(
                list(range(0, 6)) + list(range(22, 24)), n_fraud
            ),
            np.random.randint(0, 2, n_fraud),
            np.ones(n_fraud),
            np.random.uniform(0.5, 1.0, n_fraud),
            np.random.uniform(0.5, 1.0, n_fraud),
            np.random.uniform(0.5, 1.0, n_fraud),
        ])

        X = np.vstack([legit, fraud])
        y = np.concatenate([np.zeros(n_legit), np.ones(n_fraud)])
        return X, y

    # ------------------------------------------------------------------
    # Train
    # ------------------------------------------------------------------
    def train(self):
        """
        Try real DB data first, fall back to synthetic if not enough yet.
        Applies SMOTE to balance classes, then StandardScaler + RandomForest.
        """
        try:
            X, y = self._fetch_real_data()

            if X is None:
                X, y = self._get_synthetic_data()

            # Apply SMOTE only if both classes have at least 2 samples
            n_fraud = int(y.sum())
            n_legit = len(y) - n_fraud

            if n_fraud >= 2 and n_legit >= 2:
                smote = SMOTE(random_state=42)
                X, y = smote.fit_resample(X, y)
                logger.info(
                    f"✅ SMOTE applied — {len(y)} samples after resampling"
                )
            else:
                logger.warning(
                    "⚠️ Skipping SMOTE — not enough samples in both classes"
                )

            # Scale and train
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            self.model_trained = True
            logger.info("✅ Fraud model trained and ready")

        except Exception as e:
            logger.error(f"❌ Fraud model training failed: {e}")
            self.model_trained = False

    def is_model_loaded(self) -> bool:
        return self.model_trained

    # ------------------------------------------------------------------
    # Feature engineering
    # ------------------------------------------------------------------
    def _build_features(self, data: Dict[str, Any]) -> np.ndarray:
        """
        Build the feature vector from a transaction dict.
        Matches the 7 features used during training.
        """
        return np.array([[
            float(data.get("amount", 0)),
            int(data.get("hour", 12)),
            int(data.get("is_weekend", 0)),
            int(data.get("is_night", 0)),
            float(data.get("velocity_score", 0.0)),
            float(data.get("geo_anomaly_score", 0.0)),
            float(data.get("spending_deviation_score", 0.0)),
        ]])

    # ------------------------------------------------------------------
    # Predict
    # ------------------------------------------------------------------
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict fraud for a single transaction.
        Returns fraud_score, is_fraud, confidence, and action.
        """
        features = self._build_features(data)

        # Always use rule-based scoring for now (more accurate for high-value transactions)
        fraud_score = self._rule_based_score(data)

        fraud_score = round(min(max(fraud_score, 0.0), 1.0), 4)

        # Determine action and confidence based on score
        if fraud_score > 0.8:
            action, confidence = "block", "high"
        elif fraud_score > 0.5:
            action, confidence = "flag", "medium"
        elif fraud_score > 0.3:
            action, confidence = "allow", "low"
        else:
            action, confidence = "allow", "high"

        return {
            "fraud_score": fraud_score,
            "is_fraud":    fraud_score > 0.5,
            "confidence":  confidence,
            "action":      action,
        }

    # ------------------------------------------------------------------
    # Rule-based fallback
    # ------------------------------------------------------------------
    def _rule_based_score(self, data: Dict[str, Any]) -> float:
        """
        Simple rule-based scoring used when the model is not trained yet.
        Adjusted for high-value business transactions.
        """
        score = 0.0
        amount    = float(data.get("amount", 0))
        is_night  = int(data.get("is_night", 0))
        velocity  = float(data.get("velocity_score", 0))
        geo       = float(data.get("geo_anomaly_score", 0))
        deviation = float(data.get("spending_deviation_score", 0))

        # Adjusted thresholds for high-value transactions
        if amount > 1000000:  # > 1M TND
            score += 0.5
        elif amount > 500000:  # > 500K TND
            score += 0.4
        elif amount > 100000:  # > 100K TND
            score += 0.3
        elif amount > 50000:   # > 50K TND
            score += 0.2

        if is_night:
            score += 0.3

        score += np.mean([velocity, geo, deviation]) * 0.3

        return min(score, 1.0)
