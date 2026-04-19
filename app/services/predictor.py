"""
Service de prédiction ML - Cœur de l'intelligence artificielle
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import joblib
import os
from pathlib import Path
from loguru import logger
from datetime import datetime, timedelta
from typing import Dict, Any

from app.config import settings
from app.services.data_processor import DataProcessor


class DemandPredictor:
    """
    Prédicteur de demande utilisant le Machine Learning
    """
    
    def __init__(self):
        self.model = None
        self.data_processor = DataProcessor()
        self.model_path = Path(settings.ML_MODEL_PATH)
        self.model_loaded = False
    
    def load_models(self):
        """Charger les modèles pré-entraînés"""
        try:
            model_file = self.model_path / "demand_model.pkl"
            
            if model_file.exists():
                self.model = joblib.load(model_file)
                self.model_loaded = True
                logger.info(f"✅ Modèle chargé depuis {model_file}")
            else:
                # Créer un nouveau modèle si aucun n'existe
                self.model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1
                )
                self.model_loaded = True
                logger.warning("⚠️ Nouveau modèle créé (pas de modèle pré-entraîné)")
                
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle: {str(e)}")
            # Créer un modèle par défaut
            self.model = RandomForestRegressor(n_estimators=50, random_state=42)
            self.model_loaded = True
    
    def is_model_loaded(self) -> bool:
        """Vérifier si le modèle est chargé"""
        return self.model_loaded and self.model is not None
    
    def predict_next_purchase(
        self,
        df: pd.DataFrame,
        product_id: str,
        product_name: str,
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Prédire la prochaine commande pour un produit
        
        Args:
            df: DataFrame avec l'historique
            product_id: ID du produit
            product_name: Nom du produit
            days_ahead: Horizon de prédiction
            
        Returns:
            Dictionnaire avec la prédiction complète
        """
        try:
            # Feature engineering
            df_features = self.data_processor.engineer_features(df)
            
            # Calculer les statistiques de base
            avg_quantity = df['quantity'].mean()
            median_quantity = df['quantity'].median()
            std_quantity = df['quantity'].std()
            
            # Calculer l'intervalle moyen entre commandes
            if 'days_since_last' in df_features.columns and len(df_features) > 1:
                intervals = df_features['days_since_last'][df_features['days_since_last'] > 0]
                avg_interval = intervals.mean() if len(intervals) > 0 else 30
            else:
                avg_interval = 30
            
            # Prédire la quantité
            predicted_qty = self._predict_quantity(df_features, avg_quantity, median_quantity)
            
            # Prédire la date
            last_date = df['date'].max()
            predicted_date = last_date + timedelta(days=avg_interval)
            days_until = (predicted_date - datetime.now()).days
            
            # Calculer la confiance
            confidence = self._calculate_confidence(df_features)
            
            # Déterminer la tendance
            trend = self._determine_trend(df)
            
            # Détecter la saisonnalité
            seasonality = self.data_processor.detect_seasonality(df)
            
            # Calculer la qualité des données
            data_quality = self.data_processor.calculate_data_quality(df_features)
            
            # Estimer la valeur de la commande
            avg_price = df['price'].mean()
            estimated_value = predicted_qty * avg_price
            
            # Déterminer le niveau d'urgence
            urgency_level = self._determine_urgency(days_until)
            
            # Générer la recommandation
            recommendation = self._generate_recommendation(
                predicted_qty,
                days_until,
                confidence,
                trend,
                urgency_level
            )
            
            return {
                "product_id": product_id,
                "product_name": product_name,
                "predicted_quantity": round(predicted_qty, 2),
                "predicted_date": predicted_date.strftime('%Y-%m-%d'),
                "confidence": round(confidence, 3),
                "recommendation": recommendation,
                "historical_avg": round(avg_quantity, 2),
                "trend": trend,
                "days_until_order": max(0, days_until),
                "estimated_value": round(estimated_value, 2),
                "urgency_level": urgency_level,
                "data_quality": data_quality,
                "seasonality_detected": seasonality
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction: {str(e)}")
            raise
    
    def _predict_quantity(
        self,
        df: pd.DataFrame,
        avg_quantity: float,
        median_quantity: float
    ) -> float:
        """
        Prédire la quantité à commander
        
        Args:
            df: DataFrame avec features
            avg_quantity: Moyenne historique
            median_quantity: Médiane historique
            
        Returns:
            Quantité prédite
        """
        try:
            # Si pas assez de données, utiliser la médiane (plus robuste que la moyenne)
            if len(df) < 10:
                return median_quantity
            
            # Sélectionner les features pour la prédiction
            feature_cols = [
                'day_of_week', 'month', 'quarter',
                'rolling_mean_7d', 'rolling_mean_30d',
                'pct_change'
            ]
            
            # Vérifier que les features existent
            available_features = [col for col in feature_cols if col in df.columns]
            
            if len(available_features) < 3:
                # Pas assez de features, utiliser la tendance simple
                recent_avg = df['quantity'].tail(5).mean()
                return recent_avg
            
            # Préparer les données pour le modèle
            X = df[available_features].fillna(0)
            y = df['quantity']
            
            # Entraîner le modèle sur les données historiques
            if len(X) >= 10:
                try:
                    self.model.fit(X, y)
                    # Prédire sur le dernier point
                    predicted = self.model.predict(X.tail(1))[0]
                    
                    # Appliquer des limites raisonnables (éviter les valeurs aberrantes)
                    min_qty = max(0, median_quantity * 0.5)
                    max_qty = median_quantity * 2.5
                    predicted = np.clip(predicted, min_qty, max_qty)
                    
                    return predicted
                    
                except Exception as e:
                    logger.warning(f"Modèle ML échoué, utilisation de la tendance: {str(e)}")
            
            # Fallback: utiliser la tendance récente
            recent_trend = df['quantity'].tail(5).mean()
            older_trend = df['quantity'].head(5).mean()
            
            if recent_trend > older_trend:
                # Tendance à la hausse
                return recent_trend * 1.1
            elif recent_trend < older_trend:
                # Tendance à la baisse
                return recent_trend * 0.9
            else:
                # Stable
                return median_quantity
                
        except Exception as e:
            logger.warning(f"Erreur prédiction quantité: {str(e)}")
            return median_quantity
    
    def _calculate_confidence(self, df: pd.DataFrame) -> float:
        """
        Calculer le score de confiance de la prédiction (0-1)
        
        Args:
            df: DataFrame avec les données
            
        Returns:
            Score de confiance entre 0 et 1
        """
        try:
            # Facteur 1: Quantité de données (40%)
            data_points = len(df)
            data_score = min(data_points / 50, 1.0)  # Max à 50 points
            
            # Facteur 2: Régularité des commandes (30%)
            if 'days_since_last' in df.columns and len(df) > 1:
                intervals = df['days_since_last'][df['days_since_last'] > 0]
                if len(intervals) > 0:
                    std_interval = intervals.std()
                    avg_interval = intervals.mean()
                    regularity_score = 1 / (1 + (std_interval / max(avg_interval, 1)))
                else:
                    regularity_score = 0.5
            else:
                regularity_score = 0.5
            
            # Facteur 3: Stabilité des quantités (30%)
            if df['quantity'].mean() > 0:
                cv = df['quantity'].std() / df['quantity'].mean()
                stability_score = 1 / (1 + cv)
            else:
                stability_score = 0.5
            
            # Score final pondéré
            confidence = (
                data_score * 0.4 +
                regularity_score * 0.3 +
                stability_score * 0.3
            )
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.warning(f"Erreur calcul confiance: {str(e)}")
            return 0.5
    
    def _determine_trend(self, df: pd.DataFrame) -> str:
        """
        Déterminer la tendance de la demande
        
        Args:
            df: DataFrame avec les données
            
        Returns:
            "increasing", "stable", ou "decreasing"
        """
        try:
            if len(df) < 5:
                return "stable"
            
            # Comparer les moyennes récentes vs anciennes
            recent_avg = df['quantity'].tail(5).mean()
            older_avg = df['quantity'].head(5).mean()
            
            # Seuils de variation
            if recent_avg > older_avg * 1.15:
                return "increasing"
            elif recent_avg < older_avg * 0.85:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.warning(f"Erreur détermination tendance: {str(e)}")
            return "stable"
    
    def _determine_urgency(self, days_until: int) -> str:
        """
        Déterminer le niveau d'urgence
        
        Args:
            days_until: Jours avant la commande recommandée
            
        Returns:
            "urgent", "soon", ou "planned"
        """
        if days_until <= 7:
            return "urgent"
        elif days_until <= 14:
            return "soon"
        else:
            return "planned"
    
    def _generate_recommendation(
        self,
        quantity: float,
        days_until: int,
        confidence: float,
        trend: str,
        urgency: str
    ) -> str:
        """
        Générer une recommandation textuelle
        
        Args:
            quantity: Quantité prédite
            days_until: Jours avant commande
            confidence: Score de confiance
            trend: Tendance
            urgency: Niveau d'urgence
            
        Returns:
            Texte de recommandation
        """
        # Emoji d'urgence
        urgency_emoji = {
            "urgent": "🔴 URGENT",
            "soon": "🟠 BIENTÔT",
            "planned": "🟢 PLANIFIÉ"
        }[urgency]
        
        # Texte de confiance
        if confidence > 0.8:
            conf_text = "Haute confiance"
        elif confidence > 0.6:
            conf_text = "Confiance moyenne"
        else:
            conf_text = "Faible confiance - Vérifier manuellement"
        
        # Emoji de tendance
        trend_emoji = {
            "increasing": "📈 Demande en hausse",
            "decreasing": "📉 Demande en baisse",
            "stable": "➡️ Demande stable"
        }[trend]
        
        # Construire la recommandation
        qty_rounded = int(np.ceil(quantity))
        
        return (
            f"{urgency_emoji} - Commander {qty_rounded} unités d'ici {days_until} jours. "
            f"{conf_text}. {trend_emoji}."
        )
    
    def save_model(self, filename: str = "demand_model.pkl"):
        """
        Sauvegarder le modèle entraîné
        
        Args:
            filename: Nom du fichier de sauvegarde
        """
        try:
            self.model_path.mkdir(parents=True, exist_ok=True)
            model_file = self.model_path / filename
            joblib.dump(self.model, model_file)
            logger.info(f"✅ Modèle sauvegardé: {model_file}")
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde modèle: {str(e)}")
