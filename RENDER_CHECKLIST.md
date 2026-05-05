# ✅ Checklist de Déploiement Render

Utilisez cette checklist pour vous assurer que tout est prêt avant et après le déploiement.

---

## 📋 Avant le Déploiement

### Configuration du Projet

- [ ] **Code pushé sur GitHub**
  ```bash
  git add .
  git commit -m "Ready for Render"
  git push origin main
  ```

- [ ] **Fichiers nécessaires présents**
  - [ ] `render.yaml` ✅ (créé)
  - [ ] `Dockerfile` ✅ (présent)
  - [ ] `requirements.txt` ✅ (présent)
  - [ ] `.dockerignore` ✅ (présent)
  - [ ] `app/` directory ✅ (présent)

- [ ] **Tests locaux passés**
  ```bash
  # Windows
  start-ml-service.bat
  
  # Tester
  python test_integration.py
  ```

- [ ] **Variables d'environnement vérifiées**
  - [ ] `PROJECT_NAME` défini
  - [ ] `LOG_LEVEL` configuré
  - [ ] `CORS_ORIGINS` configuré pour votre frontend
  - [ ] `MIN_DATA_POINTS` = 3
  - [ ] `CONFIDENCE_THRESHOLD` = 0.6

### Configuration Render

- [ ] **Compte Render créé**
  - Aller sur [render.com](https://render.com)
  - Se connecter avec GitHub

- [ ] **Repository connecté**
  - Autoriser Render à accéder à votre repo GitHub

- [ ] **Plan choisi**
  - [ ] Free (test) - S'endort après 15 min
  - [ ] Starter ($7/mois) - Toujours actif
  - [ ] Standard ($25/mois) - Plus de ressources

---

## 🚀 Pendant le Déploiement

### Création du Service

- [ ] **Blueprint créé**
  - New + → Blueprint
  - Sélectionner le repository
  - Render détecte `render.yaml`
  - Cliquer sur "Apply"

- [ ] **Configuration vérifiée**
  - [ ] Nom du service correct
  - [ ] Région choisie (Frankfurt recommandé pour Europe)
  - [ ] Variables d'environnement chargées
  - [ ] Health check path = `/api/v1/health`

### Suivi du Build

- [ ] **Logs consultés**
  - Dashboard → Logs
  - Vérifier la construction Docker
  - Rechercher les erreurs

- [ ] **Build réussi**
  - [ ] Image Docker construite
  - [ ] Dépendances installées
  - [ ] Service démarré
  - [ ] Message: `✅ ML service ready`

---

## ✅ Après le Déploiement

### Tests de Base

- [ ] **Service accessible**
  ```bash
  curl https://votre-service.onrender.com
  ```

- [ ] **Health check OK**
  ```bash
  curl https://votre-service.onrender.com/api/v1/health
  ```
  Réponse attendue:
  ```json
  {
    "status": "healthy",
    "demand_model_loaded": true,
    "fraud_model_loaded": true,
    "version": "1.0.0"
  }
  ```

- [ ] **Documentation accessible**
  - Ouvrir: `https://votre-service.onrender.com/api/v1/docs`
  - Vérifier que Swagger UI s'affiche

### Tests Fonctionnels

- [ ] **Test automatique exécuté**
  ```bash
  python test_render_deployment.py https://votre-service.onrender.com
  ```

- [ ] **Tous les tests passent**
  - [ ] Health Check ✅
  - [ ] Root Endpoint ✅
  - [ ] Demand Prediction ✅
  - [ ] Fraud Detection ✅
  - [ ] Documentation ✅

### Tests Manuels

- [ ] **Prédiction de demande**
  - Aller sur `/api/v1/docs`
  - Tester `POST /api/v1/predict/demand`
  - Vérifier la réponse

- [ ] **Détection de fraude**
  - Tester `POST /api/v1/predict/fraud`
  - Vérifier le score de fraude

- [ ] **Batch predictions**
  - Tester `POST /api/v1/predict/batch`
  - Vérifier les résultats multiples

---

## 🔧 Configuration Post-Déploiement

### Sécurité

- [ ] **CORS configuré**
  - Remplacer `["*"]` par vos domaines spécifiques
  - Exemple: `["https://votre-frontend.com"]`

- [ ] **Variables sensibles sécurisées**
  - Utiliser Secret Files pour les clés API
  - Ne jamais exposer de secrets dans les logs

### Performance

- [ ] **Métriques surveillées**
  - Dashboard → Metrics
  - Vérifier CPU usage
  - Vérifier Memory usage

- [ ] **Logs configurés**
  - Niveau de log approprié (INFO en prod)
  - Rotation des logs activée

### Monitoring

- [ ] **Alertes configurées**
  - Dashboard → Settings → Notifications
  - [ ] Service down
  - [ ] Deploy failed
  - [ ] High memory usage

- [ ] **Uptime monitoring** (optionnel)
  - Configurer UptimeRobot ou similaire
  - Ping toutes les 5 minutes pour éviter le sleep (plan gratuit)

---

## 🔗 Intégration Frontend

### Configuration

- [ ] **URL API mise à jour**
  ```typescript
  // config.ts
  export const API_URL = 'https://votre-service.onrender.com/api/v1';
  ```

- [ ] **Variables d'environnement**
  ```env
  VITE_API_URL=https://votre-service.onrender.com/api/v1
  REACT_APP_API_URL=https://votre-service.onrender.com/api/v1
  ```

### Tests d'Intégration

- [ ] **Connexion frontend → backend**
  ```javascript
  fetch('https://votre-service.onrender.com/api/v1/health')
    .then(res => res.json())
    .then(data => console.log('✅ Connected:', data));
  ```

- [ ] **CORS fonctionnel**
  - Pas d'erreur CORS dans la console
  - Requêtes passent correctement

- [ ] **Toutes les fonctionnalités testées**
  - [ ] Prédictions de demande
  - [ ] Détection de fraude
  - [ ] Recommandations
  - [ ] Prévisions de ventes

---

## 📊 Validation Finale

### Performance

- [ ] **Temps de réponse acceptable**
  - Health check < 1s
  - Prédictions < 3s
  - Batch < 10s

- [ ] **Pas d'erreurs 500**
  - Vérifier les logs
  - Tester tous les endpoints

### Documentation

- [ ] **README mis à jour**
  - URL de production ajoutée
  - Instructions d'utilisation

- [ ] **Équipe informée**
  - URL du service partagée
  - Documentation partagée
  - Accès Render configuré

---

## 🎯 Checklist Rapide (Résumé)

Pour un déploiement rapide, vérifiez au minimum :

1. ✅ Code sur GitHub
2. ✅ `render.yaml` présent
3. ✅ Service créé sur Render
4. ✅ Build réussi
5. ✅ Health check OK
6. ✅ Documentation accessible
7. ✅ Tests passent
8. ✅ Frontend connecté

---

## 🆘 En Cas de Problème

### Service ne démarre pas
- [ ] Vérifier les logs Render
- [ ] Vérifier `Dockerfile`
- [ ] Vérifier `requirements.txt`

### Health check échoue
- [ ] Vérifier le port (doit être 8000)
- [ ] Vérifier l'endpoint `/api/v1/health`
- [ ] Augmenter le timeout

### Erreurs CORS
- [ ] Vérifier `CORS_ORIGINS` dans render.yaml
- [ ] Redéployer après modification

### Performance lente
- [ ] Passer à un plan supérieur
- [ ] Optimiser le chargement des modèles
- [ ] Ajouter du cache

---

## 📞 Ressources

- **Guide complet**: `RENDER_DEPLOYMENT_GUIDE.md`
- **Quick start**: `RENDER_QUICK_START.md`
- **Script de test**: `test_render_deployment.py`
- **Documentation Render**: [render.com/docs](https://render.com/docs)

---

## ✅ Statut Final

- [ ] **Déploiement réussi**
- [ ] **Tous les tests passent**
- [ ] **Frontend intégré**
- [ ] **Monitoring actif**
- [ ] **Équipe informée**

**Date de déploiement**: _______________

**URL du service**: _______________

**Déployé par**: _______________

---

🎉 **Félicitations ! Votre service ML est en production sur Render !**
