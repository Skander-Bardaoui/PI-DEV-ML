# Configuration Frontend - Intégration ML

## Étapes pour Intégrer la Page ML dans le Frontend

### 1. Ajouter la Route dans le Router

Ouvrir le fichier de routes principal (généralement `src/App.tsx` ou `src/routes.tsx`) et ajouter :

```typescript
import MLPredictionsPage from './pages/backoffice/purchases/MLPredictionsPage';

// Dans les routes du backoffice/purchases
{
  path: '/backoffice/purchases/ml-predictions',
  element: <MLPredictionsPage />
}
```

### 2. Ajouter le Lien dans le Menu de Navigation

Ouvrir le fichier de navigation des achats (ex: `src/components/PurchasesNav.tsx`) :

```typescript
import { SparklesIcon } from '@heroicons/react/24/outline';

// Ajouter dans les liens de navigation
<NavLink
  to="/backoffice/purchases/ml-predictions"
  className={({ isActive }) =>
    `flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
      isActive
        ? 'bg-indigo-600 text-white'
        : 'text-gray-700 hover:bg-gray-100'
    }`
  }
>
  <SparklesIcon className="h-5 w-5" />
  <span>Prédictions ML</span>
</NavLink>
```

### 3. Ajouter le Widget ML au Dashboard

Ouvrir le dashboard principal (ex: `src/pages/backoffice/purchases/PurchasesDashboard.tsx`) :

```typescript
import MLPredictionWidget from '../../../components/purchases/MLPredictionWidget';

// Dans le JSX du dashboard
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
  {/* Autres widgets */}
  
  <MLPredictionWidget />
</div>
```

### 4. Configuration de l'API URL

Vérifier que la variable d'environnement est configurée dans `.env` :

```env
VITE_API_URL=http://localhost:3000
```

### 5. Structure Complète des Fichiers Créés

```
PI-DEV-FRONT/
├── src/
│   ├── types/
│   │   └── ml-predictions.ts              ✅ Créé
│   ├── hooks/
│   │   └── useMLPredictions.ts            ✅ Créé
│   ├── components/
│   │   └── purchases/
│   │       └── MLPredictionWidget.tsx     ✅ Créé
│   └── pages/
│       └── backoffice/
│           └── purchases/
│               └── MLPredictionsPage.tsx  ✅ Créé
```

### 6. Exemple de Configuration Complète du Router

```typescript
// src/App.tsx ou src/routes.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import BackOfficeLayout from './layouts/BackOfficeLayout';
import MLPredictionsPage from './pages/backoffice/purchases/MLPredictionsPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/backoffice" element={<BackOfficeLayout />}>
          <Route path="purchases">
            {/* Routes existantes */}
            <Route path="suppliers" element={<SuppliersPage />} />
            <Route path="orders" element={<OrdersPage />} />
            
            {/* Nouvelle route ML */}
            <Route path="ml-predictions" element={<MLPredictionsPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

### 7. Exemple de Menu de Navigation Complet

```typescript
// src/components/PurchasesNav.tsx
import { NavLink } from 'react-router-dom';
import {
  ShoppingCartIcon,
  TruckIcon,
  DocumentTextIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';

export default function PurchasesNav() {
  const navItems = [
    { to: '/backoffice/purchases/suppliers', icon: ShoppingCartIcon, label: 'Fournisseurs' },
    { to: '/backoffice/purchases/orders', icon: TruckIcon, label: 'Commandes' },
    { to: '/backoffice/purchases/invoices', icon: DocumentTextIcon, label: 'Factures' },
    { to: '/backoffice/purchases/ml-predictions', icon: SparklesIcon, label: 'Prédictions ML' },
  ];

  return (
    <nav className="space-y-1">
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              isActive
                ? 'bg-indigo-600 text-white'
                : 'text-gray-700 hover:bg-gray-100'
            }`
          }
        >
          <item.icon className="h-5 w-5" />
          <span className="font-medium">{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
```

### 8. Vérification de l'Installation

Après avoir ajouté les routes et le menu :

1. Démarrer le frontend :
```bash
cd PI-DEV-FRONT
npm run dev
```

2. Naviguer vers `http://localhost:5173/backoffice/purchases/ml-predictions`

3. Vérifier que :
   - La page se charge sans erreur
   - Le widget ML apparaît sur le dashboard
   - Le lien de navigation est visible et fonctionnel
   - Les données se chargent (si le service ML est démarré)

### 9. Dépannage

#### Erreur "Module not found"

```bash
# Vérifier que tous les fichiers sont créés
ls src/types/ml-predictions.ts
ls src/hooks/useMLPredictions.ts
ls src/components/purchases/MLPredictionWidget.tsx
ls src/pages/backoffice/purchases/MLPredictionsPage.tsx
```

#### Erreur "Network Error"

Vérifier que :
- Le service ML est démarré (`http://localhost:8000`)
- Le backend NestJS est démarré (`http://localhost:3000`)
- La variable `VITE_API_URL` est correcte dans `.env`

#### Erreur "401 Unauthorized"

Vérifier que :
- L'utilisateur est connecté
- Le token JWT est valide
- Les guards d'authentification sont configurés

### 10. Personnalisation

#### Changer les Couleurs

Dans `MLPredictionsPage.tsx`, modifier les classes Tailwind :

```typescript
// Couleur principale (indigo par défaut)
className="bg-indigo-600"  // Changer en bg-blue-600, bg-purple-600, etc.

// Couleurs d'urgence
urgent: 'bg-red-100 text-red-800'    // Rouge
soon: 'bg-orange-100 text-orange-800' // Orange
planned: 'bg-green-100 text-green-800' // Vert
```

#### Ajouter des Filtres Supplémentaires

```typescript
// Ajouter un filtre par catégorie
const [categoryFilter, setCategoryFilter] = useState<string>('all');

const filteredRecommendations = recommendations?.recommendations.filter((rec) => {
  if (urgencyFilter !== 'all' && rec.urgency_level !== urgencyFilter) return false;
  if (categoryFilter !== 'all' && rec.category !== categoryFilter) return false;
  return true;
});
```

#### Modifier l'Horizon de Prédiction par Défaut

```typescript
// Dans MLPredictionsPage.tsx
const [predictionDays, setPredictionDays] = useState(60); // Au lieu de 30
```

### 11. Tests Frontend

Créer un fichier de test (optionnel) :

```typescript
// src/pages/backoffice/purchases/__tests__/MLPredictionsPage.test.tsx
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import MLPredictionsPage from '../MLPredictionsPage';

const queryClient = new QueryClient();

test('renders ML predictions page', () => {
  render(
    <QueryClientProvider client={queryClient}>
      <MLPredictionsPage />
    </QueryClientProvider>
  );
  
  expect(screen.getByText(/Prédictions ML/i)).toBeInTheDocument();
});
```

### 12. Checklist Finale

- [ ] Fichiers TypeScript créés (types, hooks, composants, pages)
- [ ] Route ajoutée dans le router
- [ ] Lien ajouté dans le menu de navigation
- [ ] Widget ajouté au dashboard (optionnel)
- [ ] Variable d'environnement configurée
- [ ] Service ML démarré et accessible
- [ ] Backend NestJS démarré
- [ ] Frontend démarré
- [ ] Page accessible et fonctionnelle
- [ ] Données chargées correctement

## Support

Pour toute question :
- Consulter `INTEGRATION_GUIDE.md` pour l'architecture complète
- Consulter `INSTALLATION.md` pour l'installation du service ML
- Vérifier les logs du navigateur (F12 > Console)
- Vérifier les logs du backend NestJS
- Vérifier les logs du service ML (`logs/ml_service.log`)
