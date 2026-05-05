# ⚡ Déploiement Rapide sur Render (5 minutes)

## 🎯 Étapes Rapides

### 1️⃣ Préparer le Code (1 min)

```bash
# Assurez-vous que tout est commité
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2️⃣ Créer le Service sur Render (2 min)

1. Allez sur [render.com](https://render.com) et connectez-vous avec GitHub
2. Cliquez sur **"New +"** → **"Blueprint"**
3. Sélectionnez votre repository
4. Render détecte automatiquement `render.yaml`
5. Cliquez sur **"Apply"**

### 3️⃣ Attendre le Déploiement (2 min)

Render va :
- ✅ Construire l'image Docker
- ✅ Déployer le service
- ✅ Exécuter le health check

### 4️⃣ Tester (30 sec)

Votre service est disponible à :
```
https://ml-prediction-service.onrender.com
```

Test rapide :
```bash
curl https://ml-prediction-service.onrender.com/api/v1/health
```

## 🎉 C'est Tout !

Votre API ML est en ligne !

**Documentation interactive** :
```
https://ml-prediction-service.onrender.com/api/v1/docs
```

---

## 🔧 Configuration Optionnelle

### Changer le Nom du Service

Dans `render.yaml`, ligne 13 :
```yaml
name: votre-nom-personnalise
```

### Configurer CORS

Dans `render.yaml`, ligne 42 :
```yaml
- key: CORS_ORIGINS
  value: '["https://votre-frontend.com"]'
```

### Passer au Plan Payant

Dans `render.yaml`, ligne 15 :
```yaml
plan: starter  # $7/mois - Pas de sleep, toujours actif
```

---

## 📊 URLs Importantes

| Service | URL |
|---------|-----|
| **API Base** | `https://ml-prediction-service.onrender.com` |
| **Health Check** | `https://ml-prediction-service.onrender.com/api/v1/health` |
| **Documentation** | `https://ml-prediction-service.onrender.com/api/v1/docs` |
| **Dashboard Render** | `https://dashboard.render.com` |

---

## 🚨 Note Importante - Plan Gratuit

Le plan gratuit s'endort après **15 minutes d'inactivité**.

**Premier appel après sleep** : ~30 secondes de délai

**Solutions** :
1. Passer au plan Starter ($7/mois) - Toujours actif
2. Utiliser un service de ping (ex: UptimeRobot)
3. Accepter le délai initial

---

## 🔗 Intégration Frontend

```typescript
// config.ts
export const API_URL = 'https://ml-prediction-service.onrender.com/api/v1';

// Test
fetch(`${API_URL}/health`)
  .then(res => res.json())
  .then(data => console.log('✅ API connectée:', data));
```

---

## 📞 Besoin d'Aide ?

Consultez le guide complet : `RENDER_DEPLOYMENT_GUIDE.md`
