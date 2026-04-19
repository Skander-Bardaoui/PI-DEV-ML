"""
Service de traitement et préparation des données
"""
import pandas as pd
import numpy as np
from typing import List
from datetime import datetime
from loguru import logger

from app.schemas.predictions import PurchaseHistoryItem


class DataProcessor:
    """Processeur de données pour le ML"""
    
    def prepare_dataframe(self, history: List[PurchaseHistoryItem]) -> pd.DataFrame:
        """
        Convertir l'historique en DataFrame pandas
        
        Args:
            history: Liste des items d'historique
            
        Returns:
            DataFrame préparé pour l'analyse
        """
        try:
            # Convertir en DataFrame
            df = pd.DataFrame([item.dict() for item in history])
            
            # Convertir les dates
            df['date'] = pd.to_datetime(df['date'])
            
            # Trier par date
            df = df.sort_values('date').reset_index(drop=True)
            
            # Supprimer les doublons
            df = df.drop_duplicates(subset=['date'], keep='last')
            
            logger.debug(f"DataFrame créé: {len(df)} lignes")
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors de la préparation du DataFrame: {str(e)}")
            raise
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Feature engineering - Créer des features pour le ML
        
        Args:
            df: DataFrame avec les données brutes
            
        Returns:
            DataFrame avec les features ajoutées
        """
        try:
            df = df.copy()
            
            # Features temporelles
            df['day_of_week'] = df['date'].dt.dayofweek
            df['day_of_month'] = df['date'].dt.day
            df['month'] = df['date'].dt.month
            df['quarter'] = df['date'].dt.quarter
            df['week_of_year'] = df['date'].dt.isocalendar().week
            df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
            df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
            
            # Jours depuis la dernière commande
            df['days_since_last'] = df['date'].diff().dt.days
            df['days_since_last'] = df['days_since_last'].fillna(0)
            
            # Features statistiques (rolling windows)
            for window in [3, 7, 14, 30]:
                if len(df) >= window:
                    df[f'rolling_mean_{window}d'] = df['quantity'].rolling(window, min_periods=1).mean()
                    df[f'rolling_std_{window}d'] = df['quantity'].rolling(window, min_periods=1).std()
                    df[f'rolling_min_{window}d'] = df['quantity'].rolling(window, min_periods=1).min()
                    df[f'rolling_max_{window}d'] = df['quantity'].rolling(window, min_periods=1).max()
            
            # Tendance (variation en pourcentage)
            df['pct_change'] = df['quantity'].pct_change()
            df['pct_change'] = df['pct_change'].fillna(0)
            
            # Lag features (valeurs précédentes)
            for lag in [1, 2, 3]:
                if len(df) > lag:
                    df[f'quantity_lag_{lag}'] = df['quantity'].shift(lag)
            
            # Features de prix
            df['price_change'] = df['price'].pct_change()
            df['price_change'] = df['price_change'].fillna(0)
            
            # Remplir les NaN
            df = df.fillna(0)
            
            logger.debug(f"Features créées: {df.shape[1]} colonnes")
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du feature engineering: {str(e)}")
            raise
    
    def detect_seasonality(self, df: pd.DataFrame) -> bool:
        """
        Détecter si les données présentent une saisonnalité
        
        Args:
            df: DataFrame avec les données
            
        Returns:
            True si saisonnalité détectée
        """
        try:
            if len(df) < 12:  # Besoin d'au moins 12 points
                return False
            
            # Grouper par mois et calculer la variance
            monthly_avg = df.groupby(df['date'].dt.month)['quantity'].mean()
            
            # Si la variance entre les mois est significative
            cv = monthly_avg.std() / monthly_avg.mean()
            
            return cv > 0.3  # Coefficient de variation > 30%
            
        except Exception as e:
            logger.warning(f"Erreur détection saisonnalité: {str(e)}")
            return False
    
    def calculate_data_quality(self, df: pd.DataFrame) -> dict:
        """
        Calculer des métriques de qualité des données
        
        Args:
            df: DataFrame avec les données
            
        Returns:
            Dictionnaire avec les métriques de qualité
        """
        try:
            # Nombre de points de données
            data_points = len(df)
            
            # Régularité des commandes (écart-type des intervalles)
            if 'days_since_last' in df.columns and len(df) > 1:
                intervals = df['days_since_last'][df['days_since_last'] > 0]
                if len(intervals) > 0:
                    avg_interval = intervals.mean()
                    std_interval = intervals.std()
                    regularity_score = 1 / (1 + (std_interval / max(avg_interval, 1)))
                else:
                    regularity_score = 0.5
            else:
                regularity_score = 0.5
            
            # Stabilité des quantités (coefficient de variation)
            if df['quantity'].mean() > 0:
                cv = df['quantity'].std() / df['quantity'].mean()
                stability_score = 1 / (1 + cv)
            else:
                stability_score = 0.5
            
            # Complétude des données
            completeness = 1 - (df.isnull().sum().sum() / (df.shape[0] * df.shape[1]))
            
            return {
                "data_points": data_points,
                "regularity_score": round(regularity_score, 3),
                "stability_score": round(stability_score, 3),
                "completeness": round(completeness, 3),
                "avg_interval_days": round(df['days_since_last'].mean(), 1) if 'days_since_last' in df.columns else None
            }
            
        except Exception as e:
            logger.warning(f"Erreur calcul qualité: {str(e)}")
            return {
                "data_points": len(df),
                "regularity_score": 0.5,
                "stability_score": 0.5,
                "completeness": 1.0
            }
    
    @staticmethod
    def get_current_timestamp() -> str:
        """Obtenir le timestamp actuel en format ISO"""
        return datetime.utcnow().isoformat() + "Z"
