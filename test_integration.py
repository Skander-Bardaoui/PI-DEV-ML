"""
Script de test pour vérifier l'intégration ML
"""
import requests
import json
from datetime import datetime, timedelta

# Configuration
ML_SERVICE_URL = "http://localhost:8000"
BACKEND_URL = "http://localhost:3000"

def test_ml_service_health():
    """Test 1: Vérifier la santé du service ML"""
    print("\n" + "="*60)
    print("TEST 1: Health Check du Service ML")
    print("="*60)
    
    try:
        response = requests.get(f"{ML_SERVICE_URL}/api/v1/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Service ML opérationnel")
            return True
        else:
            print("❌ Service ML non disponible")
            return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        print("💡 Assurez-vous que le service ML est démarré (python -m app.main)")
        return False

def test_ml_prediction():
    """Test 2: Tester une prédiction simple"""
    print("\n" + "="*60)
    print("TEST 2: Prédiction Simple")
    print("="*60)
    
    # Créer des données de test
    history = []
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(10):
        history.append({
            "date": (base_date + timedelta(days=i*10)).strftime('%Y-%m-%d'),
            "product_id": "test-product-001",
            "product_name": "Papier A4 Test",
            "quantity": 50 + (i % 3) * 5,  # Variation de 50-60
            "price": 25.5,
            "supplier": "Fournisseur Test",
            "category": "Fournitures"
        })
    
    request_data = {
        "product_id": "test-product-001",
        "history": history,
        "prediction_days": 30
    }
    
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/api/v1/predict/demand",
            json=request_data
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n📊 Résultat de la Prédiction:")
            print(f"  Produit: {result['product_name']}")
            print(f"  Quantité prédite: {result['predicted_quantity']:.2f} unités")
            print(f"  Date prédite: {result['predicted_date']}")
            print(f"  Confiance: {result['confidence']*100:.1f}%")
            print(f"  Tendance: {result['trend']}")
            print(f"  Urgence: {result['urgency_level']}")
            print(f"  Jours avant commande: {result['days_until_order']}")
            print(f"\n💡 Recommandation:")
            print(f"  {result['recommendation']}")
            print("\n✅ Prédiction réussie")
            return True
        else:
            print(f"❌ Erreur: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_batch_prediction():
    """Test 3: Tester les prédictions en batch"""
    print("\n" + "="*60)
    print("TEST 3: Prédictions en Batch")
    print("="*60)
    
    # Créer des données pour 3 produits
    products = []
    
    for prod_num in range(1, 4):
        history = []
        base_date = datetime.now() - timedelta(days=60)
        
        for i in range(6):
            history.append({
                "date": (base_date + timedelta(days=i*10)).strftime('%Y-%m-%d'),
                "product_id": f"test-product-{prod_num:03d}",
                "product_name": f"Produit Test {prod_num}",
                "quantity": 30 + prod_num * 10 + (i % 2) * 5,
                "price": 20.0 + prod_num * 5,
                "supplier": "Fournisseur Test",
                "category": "Test"
            })
        
        products.append({
            "product_id": f"test-product-{prod_num:03d}",
            "history": history
        })
    
    request_data = {
        "products": products,
        "prediction_days": 30
    }
    
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/api/v1/predict/batch",
            json=request_data
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n📊 Résultats du Batch:")
            print(f"  Total traité: {result['total_processed']}")
            print(f"  Succès: {result['successful']}")
            print(f"  Échecs: {result['failed']}")
            
            print(f"\n✅ Prédictions:")
            for pred in result['predictions']:
                print(f"  - {pred['product_name']}: {pred['predicted_quantity']:.0f} unités "
                      f"(confiance: {pred['confidence']*100:.0f}%)")
            
            if result['errors']:
                print(f"\n❌ Erreurs:")
                for error in result['errors']:
                    print(f"  - {error['product_id']}: {error['error']}")
            
            print("\n✅ Batch réussi")
            return True
        else:
            print(f"❌ Erreur: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_recommendations():
    """Test 4: Tester les recommandations"""
    print("\n" + "="*60)
    print("TEST 4: Recommandations d'Achat")
    print("="*60)
    
    # Créer des données pour plusieurs produits avec différentes urgences
    products = []
    
    # Produit urgent (dernière commande il y a 25 jours, intervalle moyen 30j)
    history1 = []
    for i in range(5):
        history1.append({
            "date": (datetime.now() - timedelta(days=25 + i*30)).strftime('%Y-%m-%d'),
            "product_id": "urgent-001",
            "product_name": "Produit Urgent",
            "quantity": 100,
            "price": 50.0,
        })
    products.append({"product_id": "urgent-001", "history": history1})
    
    # Produit bientôt (dernière commande il y a 15 jours, intervalle moyen 30j)
    history2 = []
    for i in range(5):
        history2.append({
            "date": (datetime.now() - timedelta(days=15 + i*30)).strftime('%Y-%m-%d'),
            "product_id": "soon-001",
            "product_name": "Produit Bientôt",
            "quantity": 75,
            "price": 35.0,
        })
    products.append({"product_id": "soon-001", "history": history2})
    
    request_data = {
        "products": products,
        "prediction_days": 30
    }
    
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/api/v1/recommendations",
            json=request_data
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n📋 Recommandations:")
            print(f"  Total: {result['total_recommendations']}")
            print(f"  Urgentes: {result['urgent_count']}")
            print(f"  Valeur totale: {result['total_estimated_value']:.2f} TND")
            
            print(f"\n🎯 Détails:")
            for rec in result['recommendations']:
                print(f"\n  {rec['urgency_level'].upper()}: {rec['product_name']}")
                print(f"    Quantité: {rec['predicted_quantity']:.0f} unités")
                print(f"    Dans: {rec['days_until_order']} jours")
                print(f"    Confiance: {rec['confidence']*100:.0f}%")
                print(f"    Recommandation: {rec['recommendation']}")
            
            print("\n✅ Recommandations générées")
            return True
        else:
            print(f"❌ Erreur: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_backend_integration():
    """Test 5: Tester l'intégration avec le backend NestJS"""
    print("\n" + "="*60)
    print("TEST 5: Intégration Backend NestJS")
    print("="*60)
    print("⚠️  Ce test nécessite un token d'authentification")
    print("💡 Testez manuellement avec:")
    print(f"   curl {BACKEND_URL}/purchases/ml/health")
    print(f"   curl {BACKEND_URL}/purchases/ml/recommendations -H 'Authorization: Bearer YOUR_TOKEN'")

def run_all_tests():
    """Exécuter tous les tests"""
    print("\n" + "="*60)
    print("🧪 TESTS D'INTÉGRATION ML")
    print("="*60)
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_ml_service_health()))
    
    if results[0][1]:  # Si le service est disponible
        # Test 2: Prédiction simple
        results.append(("Prédiction Simple", test_ml_prediction()))
        
        # Test 3: Batch
        results.append(("Prédictions Batch", test_batch_prediction()))
        
        # Test 4: Recommandations
        results.append(("Recommandations", test_recommendations()))
        
        # Test 5: Backend
        test_backend_integration()
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print(f"\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 Tous les tests sont passés!")
        print("\n📝 Prochaines étapes:")
        print("  1. Démarrer le backend NestJS")
        print("  2. Tester les endpoints backend avec un token")
        print("  3. Démarrer le frontend React")
        print("  4. Accéder à /backoffice/purchases/ml-predictions")
    else:
        print("\n⚠️  Certains tests ont échoué")
        print("💡 Vérifiez que le service ML est démarré:")
        print("   cd PI-DEV-ML")
        print("   python -m app.main")

if __name__ == "__main__":
    run_all_tests()
