# 🔧 Guide de Dépannage Render

Solutions aux problèmes courants lors du déploiement sur Render.

---

## 🚨 Problèmes de Build

### ❌ Build Failed - Dépendances Python

**Symptôme**: Erreur lors de `pip install`

**Solutions**:

1. **Vérifier requirements.txt**
   ```bash
   # Localement, générer un nouveau requirements.txt
   pip freeze > requirements.txt
   git add requirements.txt
   git commit -m "Update requirements"
   git push
   ```

2. **Versions incompatibles**
   ```txt
   # Dans requirements.txt, fixer les versions
   fastapi==0.109.0
   scikit-learn==1.3.0
   # Au lieu de
   fastapi>=0.109.0
   ```

3. **Dépendances système manquantes**
   ```dockerfile
   # Dans Dockerfile, ajouter
   RUN apt-get update && apt-get install -y \
       gcc \
       g++ \
       libpq-dev
   ```

### ❌ Docker Build Timeout

**Symptôme**: Build dépasse le timeout

**Solutions**:

1. **Optimiser le Dockerfile**
   ```dockerfile
   # Utiliser le cache Docker
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   # Puis copier le code
   COPY . .
   ```

2. **Réduire la taille de l'image**
   ```dockerfile
   # Utiliser une image slim
   FROM python:3.11-slim
   ```

3. **Nettoyer le cache**
   ```dockerfile
   RUN pip install --no-cache-dir -r requirements.txt
   ```

---

## 🏥 Problèmes de Health Check

### ❌ Health Check Failed

**Symptôme**: Service déployé mais health check échoue

**Solutions**:

1. **Vérifier le port**
   ```python
   # app/main.py - Doit écouter sur 0.0.0.0:8000
   if __name__ == "__main__":
       uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
   ```

2. **Vérifier l'endpoint**
   ```python
   # L'endpoint doit être exactement
   @app.get("/api/v1/health")
   async def health_check():
       return {"status": "healthy"}
   ```

3. **Augmenter le timeout**
   ```yaml
   # render.yaml
   healthCheckPath: /api/v1/health
   # Ajouter dans le dashboard Render:
   # Settings → Health Check → Timeout: 30s
   ```

4. **Vérifier les logs**
   ```bash
   # Dans Dashboard Render → Logs
   # Rechercher les erreurs au démarrage
   ```

### ❌ Service Starts Then Crashes

**Symptôme**: Service démarre puis s'arrête

**Solutions**:

1. **Vérifier les modèles ML**
   ```python
   # app/main.py
   @app.on_event("startup")
   async def startup_event():
       try:
           predictor.load_models()
           logger.info("✅ Models loaded")
       except Exception as e:
           logger.error(f"❌ Model loading failed: {e}")
           # Ne pas crash, continuer sans modèles
   ```

2. **Vérifier la mémoire**
   ```bash
   # Dashboard → Metrics
   # Si Memory > 90%, passer à un plan supérieur
   ```

3. **Lazy loading des modèles**
   ```python
   # Charger les modèles à la demande, pas au startup
   def get_model():
       if not hasattr(get_model, "model"):
           get_model.model = load_model()
       return get_model.model
   ```

---

## 🌐 Problèmes CORS

### ❌ CORS Error in Browser

**Symptôme**: `Access-Control-Allow-Origin` error

**Solutions**:

1. **Configurer CORS dans render.yaml**
   ```yaml
   - key: CORS_ORIGINS
     value: '["https://votre-frontend.com", "http://localhost:3000"]'
   ```

2. **Vérifier le middleware CORS**
   ```python
   # app/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=settings.CORS_ORIGINS,
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Redéployer après modification**
   ```bash
   git add render.yaml
   git commit -m "Fix CORS"
   git push
   ```

---

## 💾 Problèmes de Mémoire

### ❌ Out of Memory (OOM)

**Symptôme**: Service crash avec erreur mémoire

**Solutions**:

1. **Optimiser le chargement des modèles**
   ```python
   # Utiliser joblib avec compression
   import joblib
   model = joblib.load('model.pkl', mmap_mode='r')
   ```

2. **Réduire la taille des modèles**
   ```python
   # Lors de l'entraînement
   from sklearn.ensemble import RandomForestRegressor
   model = RandomForestRegressor(
       n_estimators=50,  # Au lieu de 100
       max_depth=5       # Au lieu de 10
   )
   ```

3. **Passer à un plan supérieur**
   ```yaml
   # render.yaml
   plan: standard  # 2 GB RAM au lieu de 512 MB
   ```

4. **Garbage collection manuel**
   ```python
   import gc
   
   @app.post("/predict")
   async def predict():
       result = make_prediction()
       gc.collect()  # Forcer le nettoyage
       return result
   ```

---

## 🐌 Problèmes de Performance

### ❌ Service Très Lent

**Symptôme**: Requêtes prennent > 10 secondes

**Solutions**:

1. **Profiler le code**
   ```python
   import time
   
   @app.post("/predict")
   async def predict():
       start = time.time()
       result = make_prediction()
       logger.info(f"Prediction took {time.time() - start:.2f}s")
       return result
   ```

2. **Ajouter du cache**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def get_prediction(product_id: str):
       return make_prediction(product_id)
   ```

3. **Optimiser les features**
   ```python
   # Calculer les features une seule fois
   features = compute_features(data)
   # Réutiliser pour plusieurs prédictions
   ```

4. **Utiliser des workers**
   ```dockerfile
   # Dans Dockerfile
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--workers", "2"]
   ```

### ❌ Cold Start Lent (Plan Gratuit)

**Symptôme**: Premier appel après sleep prend 30+ secondes

**Solutions**:

1. **Passer au plan Starter** ($7/mois)
   - Pas de sleep
   - Toujours actif

2. **Utiliser un service de ping**
   ```bash
   # UptimeRobot (gratuit)
   # Ping toutes les 5 minutes
   # URL: https://votre-service.onrender.com/api/v1/health
   ```

3. **Optimiser le startup**
   ```python
   # Charger les modèles en lazy loading
   @app.on_event("startup")
   async def startup_event():
       # Minimal startup, charger à la demande
       logger.info("Service ready")
   ```

---

## 🔐 Problèmes de Sécurité

### ❌ Secrets Exposés

**Symptôme**: Clés API visibles dans les logs

**Solutions**:

1. **Utiliser Secret Files**
   ```bash
   # Dashboard Render → Environment → Add Secret File
   # Créer .env avec vos secrets
   ```

2. **Ne jamais logger les secrets**
   ```python
   # ❌ Mauvais
   logger.info(f"API Key: {api_key}")
   
   # ✅ Bon
   logger.info("API Key loaded successfully")
   ```

3. **Utiliser des variables d'environnement**
   ```python
   import os
   API_KEY = os.getenv("API_KEY")  # Jamais en dur
   ```

---

## 📊 Problèmes de Logs

### ❌ Logs Manquants

**Symptôme**: Pas de logs dans le dashboard

**Solutions**:

1. **Vérifier la configuration loguru**
   ```python
   import sys
   from loguru import logger
   
   logger.remove()
   logger.add(sys.stdout, level="INFO")  # Important: sys.stdout
   ```

2. **Forcer le flush**
   ```python
   import sys
   sys.stdout.flush()
   ```

3. **Utiliser print pour debug**
   ```python
   print("DEBUG: Service starting", flush=True)
   ```

---

## 🔄 Problèmes de Déploiement

### ❌ Auto-Deploy Ne Fonctionne Pas

**Symptôme**: Push sur GitHub mais pas de redéploiement

**Solutions**:

1. **Vérifier la branche**
   ```bash
   # Dashboard → Settings → Branch
   # Doit correspondre à votre branche (main/master)
   ```

2. **Vérifier Auto-Deploy**
   ```bash
   # Dashboard → Settings
   # Auto-Deploy: ON
   ```

3. **Forcer un redéploiement**
   ```bash
   # Dashboard → Manual Deploy → Deploy Latest Commit
   ```

### ❌ Rollback Nécessaire

**Symptôme**: Nouveau déploiement cassé, besoin de revenir en arrière

**Solutions**:

1. **Via Dashboard**
   ```bash
   # Dashboard → Events
   # Cliquer sur un déploiement précédent
   # Bouton "Redeploy"
   ```

2. **Via Git**
   ```bash
   git revert HEAD
   git push origin main
   ```

---

## 🧪 Problèmes de Tests

### ❌ Tests Locaux Passent, Render Échoue

**Symptôme**: Fonctionne en local mais pas sur Render

**Solutions**:

1. **Vérifier les variables d'environnement**
   ```python
   # Ajouter des logs pour debug
   logger.info(f"CORS_ORIGINS: {settings.CORS_ORIGINS}")
   logger.info(f"LOG_LEVEL: {settings.LOG_LEVEL}")
   ```

2. **Tester avec Docker localement**
   ```bash
   docker build -t ml-service .
   docker run -p 8000:8000 ml-service
   ```

3. **Vérifier les chemins de fichiers**
   ```python
   # Utiliser des chemins relatifs
   MODEL_PATH = os.path.join(os.path.dirname(__file__), "models")
   ```

---

## 📞 Obtenir de l'Aide

### Logs Render

```bash
# Dashboard → Logs
# Filtrer par niveau: ERROR, WARNING
# Télécharger les logs pour analyse
```

### Support Render

1. **Community Forum**: [community.render.com](https://community.render.com)
2. **Discord**: [discord.gg/render](https://discord.gg/render)
3. **Documentation**: [render.com/docs](https://render.com/docs)

### Votre Équipe

1. Consulter `RENDER_DEPLOYMENT_GUIDE.md`
2. Exécuter `test_render_deployment.py`
3. Vérifier `RENDER_CHECKLIST.md`

---

## 🔍 Diagnostic Rapide

### Checklist de Debug

1. ✅ **Logs consultés** → Dashboard → Logs
2. ✅ **Health check testé** → `curl /api/v1/health`
3. ✅ **Variables vérifiées** → Dashboard → Environment
4. ✅ **Métriques consultées** → Dashboard → Metrics
5. ✅ **Tests locaux** → `docker build && docker run`

### Commandes Utiles

```bash
# Test health check
curl https://votre-service.onrender.com/api/v1/health

# Test avec verbose
curl -v https://votre-service.onrender.com/api/v1/health

# Test depuis Python
python test_render_deployment.py https://votre-service.onrender.com

# Vérifier les headers CORS
curl -H "Origin: https://votre-frontend.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://votre-service.onrender.com/api/v1/predict/demand
```

---

## 📈 Optimisations Recommandées

### Performance

1. **Cache Redis** (pour plans payants)
2. **CDN** pour assets statiques
3. **Load balancing** pour haute disponibilité
4. **Database connection pooling**

### Monitoring

1. **Sentry** pour error tracking
2. **DataDog** pour APM
3. **Prometheus** pour métriques custom

### Sécurité

1. **Rate limiting**
2. **API authentication**
3. **HTTPS only**
4. **Security headers**

---

🎯 **Besoin d'aide supplémentaire ?**

Consultez les autres guides :
- `RENDER_DEPLOYMENT_GUIDE.md` - Guide complet
- `RENDER_QUICK_START.md` - Démarrage rapide
- `RENDER_CHECKLIST.md` - Checklist complète
