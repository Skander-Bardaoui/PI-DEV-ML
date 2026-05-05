# 🚀 Guide Complet de Déploiement sur Render

Ce guide vous accompagne pas à pas pour déployer votre service ML sur Render.

## 📋 Prérequis

- Compte GitHub (pour connecter votre repo)
- Compte Render gratuit : [render.com](https://render.com)
- Code pushé sur GitHub

---

## 🎯 Étape 1 : Préparer votre Projet

### 1.1 Créer le fichier `render.yaml`

Ce fichier est déjà créé dans votre projet. Il configure automatiquement votre service.

### 1.2 Vérifier les fichiers nécessaires

✅ Fichiers déjà présents :
- `requirements.txt` - Dépendances Python
- `Dockerfile` - Configuration Docker
- `app/` - Code de l'application
- `.dockerignore` - Fichiers à exclure

---

## 🔧 Étape 2 : Configuration sur Render

### 2.1 Créer un compte Render

1. Allez sur [render.com](https://render.com)
2. Cliquez sur **"Get Started"**
3. Connectez-vous avec GitHub

### 2.2 Connecter votre Repository

1. Dans le dashboard Render, cliquez sur **"New +"**
2. Sélectionnez **"Blueprint"**
3. Connectez votre repository GitHub
4. Render détectera automatiquement le fichier `render.yaml`

### 2.3 Configuration Automatique

Render va créer automatiquement :
- ✅ Un Web Service avec Docker
- ✅ Variables d'environnement
- ✅ Health checks
- ✅ Auto-deploy sur push GitHub

---

## 🌍 Étape 3 : Variables d'Environnement

Les variables sont déjà configurées dans `render.yaml`, mais vous pouvez les modifier :

### Dans le Dashboard Render :

1. Allez dans votre service
2. Cliquez sur **"Environment"**
3. Ajoutez/modifiez les variables :

```env
PROJECT_NAME=ML Prediction Service
VERSION=1.0.0
LOG_LEVEL=INFO
ML_MODEL_PATH=models/
MIN_DATA_POINTS=3
CONFIDENCE_THRESHOLD=0.6
```

### Variables Sensibles (Secrets)

Pour les données sensibles (clés API, DB passwords) :

1. Dans Render Dashboard → **Environment**
2. Cliquez sur **"Add Secret File"**
3. Créez un fichier `.env` avec vos secrets

---

## 🚀 Étape 4 : Déploiement

### Option A : Déploiement Automatique (Recommandé)

1. Pushez votre code sur GitHub :
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

2. Render détecte automatiquement le push et déploie

### Option B : Déploiement Manuel

1. Dans le Dashboard Render
2. Cliquez sur **"Manual Deploy"**
3. Sélectionnez la branche à déployer

---

## 📊 Étape 5 : Vérification du Déploiement

### 5.1 Suivre les Logs

Dans le Dashboard Render :
- Onglet **"Logs"** pour voir le déploiement en temps réel
- Recherchez : `✅ ML service ready`

### 5.2 Tester votre API

Une fois déployé, Render vous donne une URL :
```
https://votre-service.onrender.com
```

#### Test Health Check
```bash
curl https://votre-service.onrender.com/api/v1/health
```

Réponse attendue :
```json
{
  "status": "healthy",
  "demand_model_loaded": true,
  "fraud_model_loaded": true,
  "version": "1.0.0"
}
```

#### Test Documentation API
Ouvrez dans votre navigateur :
```
https://votre-service.onrender.com/api/v1/docs
```

---

## 🔒 Étape 6 : Sécurité et CORS

### Configurer CORS pour votre Frontend

Dans `render.yaml`, modifiez la variable `CORS_ORIGINS` :

```yaml
- key: CORS_ORIGINS
  value: '["https://votre-frontend.com", "https://votre-app.vercel.app"]'
```

Ou dans le Dashboard Render → Environment :
```
CORS_ORIGINS=["https://votre-frontend.com"]
```

---

## 💰 Étape 7 : Plans et Tarification

### Plan Gratuit (Free Tier)
- ✅ 750 heures/mois
- ✅ 512 MB RAM
- ✅ Partage CPU
- ⚠️ Service s'endort après 15 min d'inactivité
- ⚠️ Redémarrage lent (~30 secondes)

### Plan Starter ($7/mois)
- ✅ Toujours actif (pas de sleep)
- ✅ 512 MB RAM
- ✅ Démarrage rapide

### Plan Standard ($25/mois)
- ✅ 2 GB RAM
- ✅ CPU dédié
- ✅ Meilleure performance ML

**Recommandation** : Commencez avec le plan gratuit pour tester, puis passez à Starter pour la production.

---

## 🔄 Étape 8 : Mises à Jour et CI/CD

### Auto-Deploy

Render redéploie automatiquement à chaque push sur la branche configurée.

### Désactiver Auto-Deploy

1. Dashboard → Settings
2. Désactivez **"Auto-Deploy"**
3. Déployez manuellement quand vous voulez

### Rollback

En cas de problème :
1. Dashboard → Events
2. Cliquez sur un déploiement précédent
3. **"Redeploy"**

---

## 🐛 Étape 9 : Dépannage

### Problème : Service ne démarre pas

**Vérifier les logs** :
1. Dashboard → Logs
2. Recherchez les erreurs Python

**Solutions courantes** :
```bash
# Dépendances manquantes
pip freeze > requirements.txt

# Port incorrect (doit être 8000)
# Vérifier dans app/main.py
```

### Problème : Health Check échoue

**Vérifier** :
- Le service écoute sur `0.0.0.0:8000`
- L'endpoint `/api/v1/health` répond
- Timeout suffisant (30s dans render.yaml)

### Problème : Service trop lent

**Solutions** :
1. Passer à un plan supérieur (plus de RAM)
2. Optimiser le chargement des modèles ML
3. Ajouter du cache

### Problème : Out of Memory

**Solutions** :
1. Réduire la taille des modèles ML
2. Utiliser `joblib` pour charger les modèles à la demande
3. Passer au plan Standard (2 GB RAM)

---

## 📈 Étape 10 : Monitoring et Performance

### Métriques Render

Dashboard → Metrics :
- CPU usage
- Memory usage
- Request count
- Response time

### Logs Personnalisés

Votre app utilise déjà `loguru` :
```python
logger.info("✅ Prediction successful")
logger.error("❌ Error occurred")
```

Consultez-les dans Dashboard → Logs

### Alertes

1. Dashboard → Settings → Notifications
2. Configurez les alertes email pour :
   - Service down
   - Deploy failed
   - High memory usage

---

## 🔗 Étape 11 : Intégration avec votre Frontend

### URL de Production

Après déploiement, utilisez l'URL Render dans votre frontend :

```typescript
// frontend/src/config.ts
export const API_URL = 'https://votre-service.onrender.com/api/v1';
```

### Variables d'Environnement Frontend

```env
# .env.production
VITE_API_URL=https://votre-service.onrender.com/api/v1
REACT_APP_API_URL=https://votre-service.onrender.com/api/v1
```

### Test d'Intégration

```bash
# Depuis votre machine
curl https://votre-service.onrender.com/api/v1/health

# Depuis votre frontend
fetch('https://votre-service.onrender.com/api/v1/health')
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 🎓 Étape 12 : Bonnes Pratiques

### 1. Utiliser des Branches

```bash
# Développement
git checkout -b develop
git push origin develop

# Production
git checkout main
git merge develop
git push origin main  # Auto-deploy sur Render
```

### 2. Variables d'Environnement

- ✅ Utilisez des variables pour tout ce qui change entre dev/prod
- ✅ Ne committez JAMAIS de secrets dans Git
- ✅ Utilisez les Secret Files de Render pour les données sensibles

### 3. Monitoring

- ✅ Activez les alertes email
- ✅ Consultez les logs régulièrement
- ✅ Surveillez l'utilisation mémoire

### 4. Performance

- ✅ Utilisez le cache pour les prédictions fréquentes
- ✅ Optimisez le chargement des modèles ML
- ✅ Considérez un CDN pour les assets statiques

---

## 📞 Support et Ressources

### Documentation Render
- [Render Docs](https://render.com/docs)
- [Blueprint Spec](https://render.com/docs/blueprint-spec)
- [Docker Deploys](https://render.com/docs/docker)

### Votre Projet
- Documentation API : `https://votre-service.onrender.com/api/v1/docs`
- Health Check : `https://votre-service.onrender.com/api/v1/health`
- Logs : Dashboard Render → Logs

### Communauté
- [Render Community](https://community.render.com)
- [Discord Render](https://discord.gg/render)

---

## ✅ Checklist Finale

Avant de déployer en production :

- [ ] Code pushé sur GitHub
- [ ] `render.yaml` configuré
- [ ] Variables d'environnement définies
- [ ] CORS configuré pour votre frontend
- [ ] Tests locaux passés
- [ ] Documentation API accessible
- [ ] Health check fonctionnel
- [ ] Monitoring activé
- [ ] Alertes configurées
- [ ] Plan Render choisi

---

## 🎉 Félicitations !

Votre service ML est maintenant déployé sur Render !

**URL de votre service** : `https://votre-service.onrender.com`

**Prochaines étapes** :
1. Intégrez l'URL dans votre frontend
2. Testez toutes les fonctionnalités
3. Surveillez les performances
4. Optimisez si nécessaire

**Besoin d'aide ?**
- Consultez les logs : Dashboard → Logs
- Vérifiez la santé : `/api/v1/health`
- Testez l'API : `/api/v1/docs`
