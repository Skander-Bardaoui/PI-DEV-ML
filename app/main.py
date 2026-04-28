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
from app.schemas.sales_predictions import (
    SalesForecastRequest,
    SalesForecastResponse,
    ClientChurnRequest,
    ClientChurnResponse,
    ProductRecommendationRequest,
    ProductRecommendationResponse
)
from app.schemas.fraud_predictions import (
    FraudTransactionInput,
    FraudPredictionOutput,
)
from app.services.predictor import DemandPredictor
from app.services.sales_predictor import SalesPredictor
from app.services.data_processor import DataProcessor
from app.services.fraud_predictor import FraudPredictor

# Logging setup
logger.remove()
logger.add(sys.stdout, level=settings.LOG_LEVEL)
logger.add(settings.LOG_FILE, rotation="500 MB", level=settings.LOG_LEVEL)

# App init
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Service de prédiction ML pour les besoins d'achat",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
predictor       = DemandPredictor()
sales_predictor = SalesPredictor()
data_processor  = DataProcessor()
fraud_predictor = FraudPredictor()


@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 Starting ML service v{settings.VERSION}")
    logger.info(f"📊 Loading models from {settings.ML_MODEL_PATH}")
    predictor.load_models()
    fraud_predictor.train()
    logger.info("✅ ML service ready")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down ML service")


@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status":  "running",
        "docs":    f"{settings.API_V1_PREFIX}/docs"
    }


@app.get(f"{settings.API_V1_PREFIX}/health")
async def health_check():
    return {
        "status":              "healthy",
        "demand_model_loaded": predictor.is_model_loaded(),
        "fraud_model_loaded":  fraud_predictor.is_model_loaded(),
        "version":             settings.VERSION
    }


# ─── Demand endpoints (unchanged) ────────────────────────────────────────────

@app.post(
    f"{settings.API_V1_PREFIX}/predict/demand",
    response_model=PredictionResponse,
    summary="Prédire la demande pour un produit",
)
async def predict_demand(request: PredictionRequest):
    try:
        logger.info(f"📊 Demand prediction for product {request.product_id}")

        if len(request.history) < settings.MIN_DATA_POINTS:
            raise HTTPException(
                status_code=400,
                detail=f"Minimum {settings.MIN_DATA_POINTS} data points required, "
                       f"{len(request.history)} provided."
            )

        df         = data_processor.prepare_dataframe(request.history)
        prediction = predictor.predict_next_purchase(
            df=df,
            product_id=request.product_id,
            product_name=request.history[0].product_name if request.history else "Product",
            days_ahead=request.prediction_days
        )

        logger.info(f"✅ Prediction: {prediction['predicted_quantity']:.2f} units")
        return prediction

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Demand prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    f"{settings.API_V1_PREFIX}/predict/batch",
    response_model=BatchPredictionResponse,
    summary="Batch predictions",
)
async def predict_batch(request: BatchPredictionRequest):
    try:
        logger.info(f"📊 Batch prediction for {len(request.products)} products")

        predictions, errors = [], []

        for product_data in request.products:
            try:
                if len(product_data.history) < settings.MIN_DATA_POINTS:
                    errors.append({
                        "product_id": product_data.product_id,
                        "error": "Insufficient data"
                    })
                    continue

                df         = data_processor.prepare_dataframe(product_data.history)
                prediction = predictor.predict_next_purchase(
                    df=df,
                    product_id=product_data.product_id,
                    product_name=product_data.history[0].product_name
                        if product_data.history else "Product",
                    days_ahead=request.prediction_days
                )
                predictions.append(prediction)

            except Exception as e:
                errors.append({"product_id": product_data.product_id, "error": str(e)})

        logger.info(f"✅ Batch done: {len(predictions)} success, {len(errors)} errors")

        return {
            "predictions":     predictions,
            "errors":          errors,
            "total_processed": len(request.products),
            "successful":      len(predictions),
            "failed":          len(errors)
        }

    except Exception as e:
        logger.error(f"❌ Batch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    f"{settings.API_V1_PREFIX}/recommendations",
    response_model=RecommendationsResponse,
    summary="Get purchase recommendations",
)
async def get_recommendations(request: BatchPredictionRequest):
    try:
        logger.info("📋 Generating recommendations")

        batch_result    = await predict_batch(request)
        recommendations = [
            pred for pred in batch_result["predictions"]
            if pred["confidence"] >= settings.CONFIDENCE_THRESHOLD
            and pred["days_until_order"] <= 30
        ]
        recommendations.sort(key=lambda x: x["days_until_order"])

        urgent_count = len([r for r in recommendations if r["days_until_order"] <= 7])
        total_value  = sum(r.get("estimated_value", 0) for r in recommendations)

        logger.info(
            f"✅ {len(recommendations)} recommendations "
            f"({urgent_count} urgent)"
        )

        return {
            "recommendations":       recommendations,
            "total_recommendations": len(recommendations),
            "urgent_count":          urgent_count,
            "total_estimated_value": total_value,
            "generated_at":          data_processor.get_current_timestamp()
        }

    except Exception as e:
        logger.error(f"❌ Recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Sales endpoints (unchanged) ─────────────────────────────────────────────

@app.post(
    f"{settings.API_V1_PREFIX}/sales/forecast",
    response_model=SalesForecastResponse,
    summary="Prédire les ventes futures",
)
async def forecast_sales(request: SalesForecastRequest):
    try:
        logger.info(f"📊 Sales forecast for {request.forecast_days} days")

        if len(request.sales_history) < 3:
            raise HTTPException(
                status_code=400,
                detail="Minimum 3 history entries required"
            )

        history  = [item.dict() for item in request.sales_history]
        forecast = sales_predictor.predict_sales_forecast(
            sales_history=history,
            forecast_days=request.forecast_days
        )

        logger.info(
            f"✅ Forecast: {forecast['predicted_sales']:.2f} DT "
            f"over {request.forecast_days} days"
        )
        return forecast

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Sales forecast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    f"{settings.API_V1_PREFIX}/sales/churn",
    response_model=ClientChurnResponse,
    summary="Prédire le risque de perte d'un client",
)
async def predict_churn(request: ClientChurnRequest):
    try:
        logger.info(f"📊 Churn analysis for client {request.client_id}")

        if len(request.client_history) < 2:
            raise HTTPException(
                status_code=400,
                detail="Minimum 2 purchases required for churn analysis"
            )

        history        = [item.dict() for item in request.client_history]
        churn_analysis = sales_predictor.predict_client_churn(history)
        churn_analysis["client_id"] = request.client_id

        logger.info(f"✅ Churn risk: {churn_analysis['churn_risk_score']:.3f}")
        return churn_analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Churn prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    f"{settings.API_V1_PREFIX}/sales/recommendations",
    response_model=ProductRecommendationResponse,
    summary="Recommander des produits à un client",
)
async def recommend_products(request: ProductRecommendationRequest):
    try:
        logger.info(f"📊 Product recommendations for client {request.client_id}")

        purchases       = [item.dict() for item in request.client_purchases]
        products        = [item.dict() for item in request.available_products]
        recommendations = sales_predictor.recommend_products(
            client_purchases=purchases,
            all_products=products
        )

        logger.info(f"✅ {len(recommendations)} products recommended")

        return {
            "client_id":             request.client_id,
            "recommendations":       recommendations,
            "total_recommendations": len(recommendations)
        }

    except Exception as e:
        logger.error(f"❌ Recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Fraud endpoint (NEW) ─────────────────────────────────────────────────────

@app.post(
    f"{settings.API_V1_PREFIX}/predict/fraud",
    response_model=FraudPredictionOutput,
    summary="Détecter une transaction frauduleuse",
    description="Analyse une transaction et retourne un score de risque de fraude"
)
async def predict_fraud(request: FraudTransactionInput):
    try:
        logger.info(f"🔍 Fraud check — amount: {request.amount}")
        result = fraud_predictor.predict(request.dict())
        emoji  = "🚨" if result["is_fraud"] else "✅"
        logger.info(
            f"{emoji} Score: {result['fraud_score']} "
            f"| Action: {result['action']}"
        )
        return result

    except Exception as e:
        logger.error(f"❌ Fraud prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    f"{settings.API_V1_PREFIX}/fraud/retrain",
    summary="Ré-entraîner le modèle de fraude",
    description="Déclenche un ré-entraînement sur les dernières données labellisées"
)
async def retrain_fraud_model():
    """
    Call this endpoint after your team has reviewed and labeled
    flagged transactions (fraud_reviewed = true in the DB).
    The model will retrain on the updated real data.
    """
    try:
        logger.info("🔄 Retraining fraud model on demand...")
        fraud_predictor.train()
        return {
            "status":       "success",
            "model_ready":  fraud_predictor.is_model_loaded(),
            "message":      "Fraud model retrained successfully"
        }
    except Exception as e:
        logger.error(f"❌ Retrain error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Global error handler ─────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
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
