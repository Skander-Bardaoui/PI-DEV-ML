"""
FastAPI Application - ML Service
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from app.config import settings
from app.schemas.predictions import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    RecommendationsResponse
)
from app.services.predictor import DemandPredictor
from app.services.data_processor import DataProcessor

# Configuration des logs
logger.remove()
logger.add(sys.stdout, level=settings.LOG_LEVEL)
logger.add(settings.LOG_FILE, rotation="500 MB", level=settings.LOG_LEVEL)

# Initialisation de l'application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Service de prédiction ML pour les besoins d'achat",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation des services
predictor = DemandPredictor()
data_processor = DataProcessor()


@app.on_event("startup")
async def startup_event():
    """Événement au démarrage de l'application"""
    logger.info(f"🚀 Démarrage du service ML v{settings.VERSION}")
    logger.info(f"📊 Chargement des modèles depuis {settings.ML_MODEL_PATH}")
    predictor.load_models()
    logger.info("✅ Service ML prêt")


@app.on_event("shutdown")
async def shutdown_event():
    """Événement à l'arrêt de l'application"""
    logger.info("🛑 Arrêt du service ML")


@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }


@app.get(f"{settings.API_V1_PREFIX}/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": predictor.is_model_loaded(),
        "version": settings.VERSION
    }


@app.post(
    f"{settings.API_V1_PREFIX}/predict/demand",
    response_model=PredictionResponse,
    summary="Prédire la demande pour un produit",
    description="Analyse l'historique d'achat et prédit les besoins futurs"
)
async def predict_demand(request: PredictionRequest):
    """
    Prédire les besoins d'achat pour un produit spécifique
    
    - **product_id**: ID du produit
    - **history**: Historique des achats
    - **prediction_days**: Horizon de prédiction (défaut: 30 jours)
    """
    try:
        logger.info(f"📊 Prédiction demandée pour produit {request.product_id}")
        
        # Validation des données
        if len(request.history) < settings.MIN_DATA_POINTS:
            raise HTTPException(
                status_code=400,
                detail=f"Données insuffisantes. Minimum {settings.MIN_DATA_POINTS} points requis, {len(request.history)} fournis."
            )
        
        # Traitement des données
        df = data_processor.prepare_dataframe(request.history)
        
        # Prédiction
        prediction = predictor.predict_next_purchase(
            df=df,
            product_id=request.product_id,
            product_name=request.history[0].product_name if request.history else "Produit",
            days_ahead=request.prediction_days
        )
        
        logger.info(f"✅ Prédiction réussie: {prediction['predicted_quantity']:.2f} unités")
        return prediction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la prédiction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")


@app.post(
    f"{settings.API_V1_PREFIX}/predict/batch",
    response_model=BatchPredictionResponse,
    summary="Prédictions en batch",
    description="Prédire pour plusieurs produits simultanément"
)
async def predict_batch(request: BatchPredictionRequest):
    """
    Prédire les besoins pour plusieurs produits en une seule requête
    """
    try:
        logger.info(f"📊 Prédiction batch pour {len(request.products)} produits")
        
        predictions = []
        errors = []
        
        for product_data in request.products:
            try:
                if len(product_data.history) < settings.MIN_DATA_POINTS:
                    errors.append({
                        "product_id": product_data.product_id,
                        "error": "Données insuffisantes"
                    })
                    continue
                
                df = data_processor.prepare_dataframe(product_data.history)
                prediction = predictor.predict_next_purchase(
                    df=df,
                    product_id=product_data.product_id,
                    product_name=product_data.history[0].product_name if product_data.history else "Produit",
                    days_ahead=request.prediction_days
                )
                predictions.append(prediction)
                
            except Exception as e:
                errors.append({
                    "product_id": product_data.product_id,
                    "error": str(e)
                })
        
        logger.info(f"✅ Batch terminé: {len(predictions)} succès, {len(errors)} erreurs")
        
        return {
            "predictions": predictions,
            "errors": errors,
            "total_processed": len(request.products),
            "successful": len(predictions),
            "failed": len(errors)
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur batch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    f"{settings.API_V1_PREFIX}/recommendations",
    response_model=RecommendationsResponse,
    summary="Obtenir les recommandations d'achat",
    description="Retourne les produits à commander en priorité"
)
async def get_recommendations(request: BatchPredictionRequest):
    """
    Générer des recommandations d'achat basées sur les prédictions
    
    Retourne uniquement les produits:
    - Avec une confiance >= seuil configuré
    - À commander dans les 30 prochains jours
    - Triés par urgence
    """
    try:
        logger.info("📋 Génération des recommandations")
        
        # Obtenir toutes les prédictions
        batch_result = await predict_batch(request)
        
        # Filtrer et trier les recommandations
        recommendations = [
            pred for pred in batch_result["predictions"]
            if pred["confidence"] >= settings.CONFIDENCE_THRESHOLD
            and pred["days_until_order"] <= 30
        ]
        
        # Trier par urgence (date la plus proche en premier)
        recommendations.sort(key=lambda x: x["days_until_order"])
        
        # Calculer les statistiques
        urgent_count = len([r for r in recommendations if r["days_until_order"] <= 7])
        total_value = sum(r.get("estimated_value", 0) for r in recommendations)
        
        logger.info(f"✅ {len(recommendations)} recommandations générées ({urgent_count} urgentes)")
        
        return {
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "urgent_count": urgent_count,
            "total_estimated_value": total_value,
            "generated_at": data_processor.get_current_timestamp()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur recommandations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire global des exceptions"""
    logger.error(f"❌ Exception non gérée: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erreur interne du serveur",
            "error": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
