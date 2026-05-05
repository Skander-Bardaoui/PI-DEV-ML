# 🏗️ Architecture de Déploiement Render

## 📊 Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                         UTILISATEURS                             │
│                    (Frontend / API Clients)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      RENDER PLATFORM                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Load Balancer                          │  │
│  │              (Automatic HTTPS/SSL)                        │  │
│  └─────────────────────────┬─────────────────────────────────┘  │
│                            │                                     │
│  ┌─────────────────────────▼─────────────────────────────────┐  │
│  │              ML Service Container                         │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │         FastAPI Application                         │ │  │
│  │  │                                                     │ │  │
│  │  │  • Health Check: /api/v1/health                    │ │  │
│  │  │  • Demand Prediction: /api/v1/predict/demand       │ │  │
│  │  │  • Fraud Detection: /api/v1/predict/fraud          │ │  │
│  │  │  • Sales Forecast: /api/v1/sales/forecast          │ │  │
│  │  │  • Documentation: /api/v1/docs                     │ │  │
│  │  │                                                     │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │         ML Models & Services                        │ │  │
│  │  │                                                     │ │  │
│  │  │  • DemandPredictor (Random Forest)                 │ │  │
│  │  │  • FraudPredictor (Isolation Forest)               │ │  │
│  │  │  • SalesPredictor (Time Series)                    │ │  │
│  │  │  • DataProcessor (Feature Engineering)             │ │  │
│  │  │                                                     │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │                                                           │  │
│  │  Resources:                                               │  │
│  │  • CPU: Shared (Free) / Dedicated (Paid)                 │  │
│  │  • RAM: 512 MB (Free/Starter) / 2 GB (Standard)          │  │
│  │  • Storage: Ephemeral (models loaded at startup)         │  │
│  │                                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Monitoring & Logs                            │  │
│  │                                                           │  │
│  │  • Real-time Logs                                        │  │
│  │  • Metrics (CPU, Memory, Requests)                       │  │
│  │  • Deploy History                                        │  │
│  │  • Health Check Status                                   │  │
│  │                                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flux de Déploiement

```
┌──────────────┐
│   GitHub     │
│  Repository  │
└──────┬───────┘
       │
       │ git push
       │
       ▼
┌──────────────┐
│   Render     │
│  Webhook     │  ← Détecte le push automatiquement
└──────┬───────