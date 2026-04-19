<<<<<<< HEAD
# 🤖 Service ML - Prédiction des Besoins d'Achat

Service de Machine Learning pour prédire intelligemment les besoins d'achat futurs en analysant l'historique des commandes.

## 🎯 Fonctionnalités

- ✅ Prédiction de la quantité à commander
- ✅ Prédiction de la date de commande optimale
- ✅ Calcul du score de confiance (0-100%)
- ✅ Détection de tendance (hausse/baisse/stable)
- ✅ Détection de saisonnalité
- ✅ Recommandations d'achat intelligentes avec niveaux d'urgence
- ✅ Support des prédictions en batch (plusieurs produits)
- ✅ API REST complète avec documentation Swagger
- ✅ Logging avancé et monitoring

## 🚀 Quick Start

```bash
# 1. Installation
cd PI-DEV-ML
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. Configuration
cp .env.example .env
mkdir models logs

# 3. Démarrage
python -m app.main
```

✅ Service disponible sur `http://localhost:8000`

📚 Documentation interactive : `http://localhost:8000/api/v1/docs`

## 📖 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Démarrage en 5 minutes
- **[INSTALLATION.md](INSTALLATION.md)** - Installation détaillée
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Architecture et intégration complète
- **[FRONTEND_SETUP.md](FRONTEND_SETUP.md)** - Configuration du frontend React

## 🛠️ Technologies

| Technologie | Usage | Version |
|------------|-------|---------|
| **FastAPI** | Framework web Python | 0.115.0+ |
| **scikit-learn** | Algorithmes ML (Random Forest) | 1.5.0+ |
| **pandas** | Manipulation de données | 2.2.0+ |
| **numpy** | Calculs numériques | 1.26.0+ |
| **pydantic** | Validation des données | 2.10.0+ |
| **loguru** | Logging avancé | 0.7.0+ |

## 📊 Algorithmes ML

### Feature Engineering Automatique

Le système crée automatiquement des features avancées :

1. **Features temporelles**
   - Jour de la semaine (0-6)
   - Mois (1-12)
   - Trimestre (1-4)

2. **Rolling windows**
   - Moyenne mobile 7 jours
   - Moyenne mobile 30 jours

3. **Lag features**
   - Quantité précédente (lag 1)
   - Quantité il y a 2 commandes (lag 2)

4. **Variations**
   - Pourcentage de changement
   - Jours depuis dernière commande

### Modèle de Prédiction

- **Algorithme** : Random Forest Regressor
- **Paramètres** :
  - 100 arbres de décision
  - Profondeur maximale : 10
  - Échantillons min pour split : 5
  - Échantillons min par feuille : 2

### Score de Confiance

Calculé sur 3 facteurs pondérés :
- **Quantité de données (40%)** : Plus de données = plus de confiance
- **Régularité des commandes (30%)** : Intervalles réguliers = plus de confiance
- **Stabilité des quantités (30%)** : Quantités stables = plus de confiance

## 🔌 API Endpoints

### Health Check
```http
GET /api/v1/health
```

### Prédiction Simple
```http
POST /api/v1/predict/demand
Content-Type: application/json

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
  ],
  "prediction_days": 30
}
```

### Prédictions en Batch
```http
POST /api/v1/predict/batch
Content-Type: application/json

{
  "products": [
    {
      "product_id": "prod-123",
      "history": [...]
    }
  ],
  "prediction_days": 30
}
```

### Recommandations d'Achat
```http
POST /api/v1/recommendations
Content-Type: application/json

{
  "products": [...],
  "prediction_days": 30
}
```

## 📁 Structure du Projet

```
PI-DEV-ML/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Application FastAPI
│   ├── config.py                  # Configuration avec Pydantic
│   ├── schemas/
│   │   └── predictions.py         # Schémas Pydantic (validation)
│   └── services/
│       ├── predictor.py           # Algorithmes ML (cœur de l'IA)
│       └── data_processor.py      # Traitement et feature engineering
├── models/                        # Modèles ML sauvegardés
├── logs/                          # Logs de l'application
├── requirements.txt               # Dépendances Python
├── .env.example                   # Configuration exemple
├── README.md                      # Ce fichier
├── QUICK_START.md                 # Démarrage rapide
├── INSTALLATION.md                # Guide d'installation
├── INTEGRATION_GUIDE.md           # Guide d'intégration
├── FRONTEND_SETUP.md              # Setup frontend
└── test_integration.py            # Tests d'intégration
```

## 🧪 Tests

```bash
# Exécuter les tests d'intégration
python test_integration.py
```

Tests inclus :
- ✅ Health check du service
- ✅ Prédiction simple
- ✅ Prédictions en batch
- ✅ Recommandations d'achat

## 🔗 Intégration

Ce service ML s'intègre avec :

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Frontend      │      │   Backend       │      │   Service ML    │
│   React         │─────▶│   NestJS        │─────▶│   FastAPI       │
│                 │      │                 │      │   Python        │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

### Backend NestJS
- Service : `ml-prediction.service.ts`
- Contrôleur : `ml-prediction.controller.ts`
- DTOs : `ml-prediction.dto.ts`

### Frontend React
- Page : `MLPredictionsPage.tsx`
- Widget : `MLPredictionWidget.tsx`
- Hooks : `useMLPredictions.ts`
- Types : `ml-predictions.ts`

## 📈 Métriques et Indicateurs

### Niveaux d'Urgence

| Niveau | Délai | Badge |
|--------|-------|-------|
| **URGENT** | ≤ 7 jours | 🔴 |
| **BIENTÔT** | 8-14 jours | 🟠 |
| **PLANIFIÉ** | ≥ 15 jours | 🟢 |

### Score de Confiance

| Score | Niveau | Couleur |
|-------|--------|---------|
| > 80% | Haute confiance | 🟢 Vert |
| 60-80% | Confiance moyenne | 🟡 Jaune |
| < 60% | Faible confiance | 🔴 Rouge |

### Tendances

| Tendance | Icône | Description |
|----------|-------|-------------|
| **Increasing** | 📈 | Demande en hausse (+15%) |
| **Stable** | ➡️ | Demande stable (±15%) |
| **Decreasing** | 📉 | Demande en baisse (-15%) |

## ⚙️ Configuration

Fichier `.env` :

```env
# Service
PROJECT_NAME=ML Prediction Service
VERSION=1.0.0
LOG_LEVEL=INFO
LOG_FILE=logs/ml_service.log

# ML
ML_MODEL_PATH=models/
MIN_DATA_POINTS=3
CONFIDENCE_THRESHOLD=0.6

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

## 🐛 Dépannage

### Service ne démarre pas

```bash
# Vérifier Python
python --version  # Doit être 3.9+

# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Erreur "Port already in use"

```bash
# Changer le port
uvicorn app.main:app --port 8001
```

### Pas de prédictions

Vérifier que :
- Minimum 3 achats par produit
- Dates au format YYYY-MM-DD
- Quantités > 0

## 📝 Logs

Les logs sont enregistrés dans `logs/ml_service.log`

```bash
# Voir les logs en temps réel
tail -f logs/ml_service.log
```

## 🎓 Améliorations Futures

- [ ] Prophet pour la saisonnalité avancée
- [ ] LSTM pour les séries temporelles
- [ ] XGBoost pour plus de précision
- [ ] Cache des prédictions
- [ ] Entraînement automatique
- [ ] A/B testing des modèles
- [ ] Intégration avec les jours fériés
- [ ] Optimisation des stocks

## 📄 Licence

Propriétaire - Tous droits réservés

## 🤝 Support

Pour toute question :
1. Consulter la documentation dans les fichiers `.md`
2. Vérifier les logs : `logs/ml_service.log`
3. Tester avec : `python test_integration.py`
4. Documentation API : `http://localhost:8000/api/v1/docs`
=======
# PI-DEV-ML
>>>>>>> 7555a628f65455befd2cf93ca8ffddf6d94c8fec
