"""
Service de prédiction ML pour les Ventes
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from typing import Dict, Any, List
from loguru import logger

from app.services.data_processor import DataProcessor


class SalesPredictor:
    """
    Prédicteur de ventes utilisant le Machine Learning
    """
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        self.data_processor = DataProcessor()
    
    def predict_sales_forecast(
        self,
        sales_history: List[Dict],
        forecast_days: int = 30
    ) -> Dict[str, Any]:
        """
        Prédire les ventes futures
        
        Args:
            sales_history: Historique des ventes [{date, amount, quantity}]
            forecast_days: Nombre de jours à prédire
            
        Returns:
            Prédictions avec tendances et insights
        """
        try:
            # Convertir en DataFrame
            df = pd.DataFrame(sales_history)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculer les statistiques
            total_sales = df['amount'].sum()
            avg_daily_sales = df['amount'].mean()
            trend = self._calculate_trend(df)
            
            # Prédire les ventes futures
            predicted_amount = self._predict_future_sales(df, forecast_days)
            
            # Calculer la confiance
            confidence = self._calculate_confidence(df)
            
            # Identifier les meilleurs jours
            best_days = self._identify_best_days(df)
            
            # Détecter la saisonnalité
            seasonality = self._detect_seasonality(df)
            
            return {
                "forecast_days": forecast_days,
                "predicted_sales": round(predicted_amount, 2),
                "predicted_daily_avg": round(predicted_amount / forecast_days, 2),
                "current_daily_avg": round(avg_daily_sales, 2),
                "trend": trend,
                "confidence": round(confidence, 3),
                "best_selling_days": best_days,
                "seasonality_detected": seasonality,
                "growth_rate": self._calculate_growth_rate(df),
                "recommendation": self._generate_sales_recommendation(
                    predicted_amount,
                    avg_daily_sales,
                    trend,
                    confidence
                )
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction ventes: {str(e)}")
            raise
    
    def predict_client_churn(
        self,
        client_history: List[Dict]
    ) -> Dict[str, Any]:
        """
        Prédire le risque de perte d'un client
        
        Args:
            client_history: Historique d'achats du client
            
        Returns:
            Score de risque et recommandations
        """
        try:
            df = pd.DataFrame(client_history)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculer les métriques
            days_since_last = (datetime.now() - df['date'].max()).days
            avg_interval = self._calculate_avg_interval(df)
            purchase_frequency = len(df) / ((df['date'].max() - df['date'].min()).days / 30)
            
            # Calculer le score de risque (0-1)
            churn_risk = self._calculate_churn_risk(
                days_since_last,
                avg_interval,
                purchase_frequency
            )
            
            # Déterminer le niveau de risque
            risk_level = "high" if churn_risk > 0.7 else "medium" if churn_risk > 0.4 else "low"
            
            return {
                "churn_risk_score": round(churn_risk, 3),
                "risk_level": risk_level,
                "days_since_last_purchase": days_since_last,
                "average_purchase_interval": round(avg_interval, 1),
                "purchase_frequency_per_month": round(purchase_frequency, 2),
                "recommendation": self._generate_churn_recommendation(churn_risk, days_since_last)
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction churn: {str(e)}")
            raise
    
    def recommend_products(
        self,
        client_purchases: List[Dict],
        all_products: List[Dict]
    ) -> List[Dict]:
        """
        Recommander des produits à un client
        
        Args:
            client_purchases: Achats du client
            all_products: Tous les produits disponibles
            
        Returns:
            Liste de produits recommandés
        """
        try:
            # Extraire les produits déjà achetés
            purchased_ids = set(p['product_id'] for p in client_purchases)
            
            # Calculer les catégories préférées
            categories = [p.get('category') for p in client_purchases if p.get('category')]
            preferred_categories = pd.Series(categories).value_counts().head(3).index.tolist()
            
            # Filtrer et scorer les produits
            recommendations = []
            for product in all_products:
                if product['id'] not in purchased_ids:
                    score = 0
                    
                    # Bonus si dans catégorie préférée
                    if product.get('category') in preferred_categories:
                        score += 0.5
                    
                    # Bonus si prix similaire
                    avg_price = np.mean([p['price'] for p in client_purchases])
                    price_diff = abs(product['price'] - avg_price) / avg_price
                    if price_diff < 0.3:
                        score += 0.3
                    
                    # Bonus si populaire
                    if product.get('popularity', 0) > 0.7:
                        score += 0.2
                    
                    if score > 0.3:
                        recommendations.append({
                            "product_id": product['id'],
                            "product_name": product['name'],
                            "score": round(score, 3),
                            "reason": self._generate_recommendation_reason(score, product, preferred_categories)
                        })
            
            # Trier par score
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:5]
            
        except Exception as e:
            logger.error(f"❌ Erreur recommandations produits: {str(e)}")
            return []
    
    def _predict_future_sales(self, df: pd.DataFrame, days: int) -> float:
        """Prédire les ventes futures"""
        try:
            # Utiliser la tendance récente
            recent_sales = df.tail(30)['amount'].mean()
            older_sales = df.head(30)['amount'].mean() if len(df) > 30 else recent_sales
            
            # Calculer le taux de croissance
            if older_sales > 0:
                growth_rate = (recent_sales - older_sales) / older_sales
            else:
                growth_rate = 0
            
            # Prédire avec la tendance
            predicted = recent_sales * days * (1 + growth_rate)
            
            return max(0, predicted)
            
        except Exception as e:
            logger.warning(f"Erreur prédiction: {str(e)}")
            return df['amount'].mean() * days
    
    def _calculate_trend(self, df: pd.DataFrame) -> str:
        """Calculer la tendance des ventes"""
        try:
            if len(df) < 10:
                return "stable"
            
            recent = df.tail(int(len(df) * 0.3))['amount'].mean()
            older = df.head(int(len(df) * 0.3))['amount'].mean()
            
            if recent > older * 1.15:
                return "increasing"
            elif recent < older * 0.85:
                return "decreasing"
            else:
                return "stable"
                
        except:
            return "stable"
    
    def _calculate_confidence(self, df: pd.DataFrame) -> float:
        """Calculer le score de confiance"""
        try:
            # Plus de données = plus de confiance
            data_score = min(len(df) / 100, 1.0)
            
            # Stabilité des ventes
            if df['amount'].mean() > 0:
                cv = df['amount'].std() / df['amount'].mean()
                stability_score = 1 / (1 + cv)
            else:
                stability_score = 0.5
            
            return (data_score * 0.6 + stability_score * 0.4)
            
        except:
            return 0.5
    
    def _identify_best_days(self, df: pd.DataFrame) -> List[str]:
        """Identifier les meilleurs jours de vente"""
        try:
            df['day_of_week'] = df['date'].dt.day_name()
            day_sales = df.groupby('day_of_week')['amount'].mean().sort_values(ascending=False)
            return day_sales.head(3).index.tolist()
        except:
            return []
    
    def _detect_seasonality(self, df: pd.DataFrame) -> bool:
        """Détecter la saisonnalité"""
        try:
            if len(df) < 30:
                return False
            
            df['month'] = df['date'].dt.month
            monthly_sales = df.groupby('month')['amount'].mean()
            
            # Si variation > 30% entre mois, il y a saisonnalité
            variation = (monthly_sales.max() - monthly_sales.min()) / monthly_sales.mean()
            return variation > 0.3
            
        except:
            return False
    
    def _calculate_growth_rate(self, df: pd.DataFrame) -> float:
        """Calculer le taux de croissance"""
        try:
            if len(df) < 10:
                return 0.0
            
            recent = df.tail(int(len(df) * 0.3))['amount'].mean()
            older = df.head(int(len(df) * 0.3))['amount'].mean()
            
            if older > 0:
                return round((recent - older) / older * 100, 2)
            return 0.0
            
        except:
            return 0.0
    
    def _calculate_avg_interval(self, df: pd.DataFrame) -> float:
        """Calculer l'intervalle moyen entre achats"""
        try:
            if len(df) < 2:
                return 30.0
            
            intervals = df['date'].diff().dt.days.dropna()
            return intervals.mean()
            
        except:
            return 30.0
    
    def _calculate_churn_risk(
        self,
        days_since_last: int,
        avg_interval: float,
        frequency: float
    ) -> float:
        """Calculer le risque de churn"""
        try:
            # Facteur 1: Temps depuis dernier achat
            if avg_interval > 0:
                time_factor = min(days_since_last / (avg_interval * 2), 1.0)
            else:
                time_factor = 0.5
            
            # Facteur 2: Fréquence d'achat
            freq_factor = 1 - min(frequency / 4, 1.0)  # 4 achats/mois = faible risque
            
            # Score final
            return (time_factor * 0.7 + freq_factor * 0.3)
            
        except:
            return 0.5
    
    def _generate_sales_recommendation(
        self,
        predicted: float,
        current_avg: float,
        trend: str,
        confidence: float
    ) -> str:
        """Générer une recommandation de ventes"""
        trend_emoji = {
            "increasing": "📈 Tendance positive",
            "decreasing": "📉 Tendance négative",
            "stable": "➡️ Tendance stable"
        }[trend]
        
        if predicted > current_avg * 30:
            action = "Augmenter les stocks et préparer plus de ressources"
        elif predicted < current_avg * 20:
            action = "Réduire les stocks et optimiser les coûts"
        else:
            action = "Maintenir le niveau actuel"
        
        conf_text = "Haute confiance" if confidence > 0.7 else "Confiance moyenne"
        
        return f"{trend_emoji}. {action}. {conf_text} dans la prédiction."
    
    def _generate_churn_recommendation(self, risk: float, days: int) -> str:
        """Générer une recommandation anti-churn"""
        if risk > 0.7:
            return f"🔴 URGENT: Client inactif depuis {days} jours. Contacter immédiatement avec une offre spéciale."
        elif risk > 0.4:
            return f"🟠 ATTENTION: Risque modéré. Envoyer un email de relance ou proposer une promotion."
        else:
            return f"🟢 Client actif. Continuer l'engagement régulier."
    
    def _generate_recommendation_reason(
        self,
        score: float,
        product: Dict,
        preferred_categories: List[str]
    ) -> str:
        """Générer la raison de la recommandation"""
        reasons = []
        
        if product.get('category') in preferred_categories:
            reasons.append("catégorie préférée")
        
        if product.get('popularity', 0) > 0.7:
            reasons.append("produit populaire")
        
        if score > 0.7:
            reasons.append("forte correspondance")
        
        return "Recommandé car: " + ", ".join(reasons) if reasons else "Produit suggéré"
