"""
Test Script pour vérifier le déploiement Render
Usage: python test_render_deployment.py <URL_DE_VOTRE_SERVICE>
Exemple: python test_render_deployment.py https://ml-prediction-service.onrender.com
"""

import sys
import requests
from datetime import datetime, timedelta
from colorama import init, Fore, Style

init(autoreset=True)

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}{text:^60}")
    print(f"{Fore.CYAN}{'='*60}\n")

def print_success(text):
    print(f"{Fore.GREEN}✅ {text}")

def print_error(text):
    print(f"{Fore.RED}❌ {text}")

def print_info(text):
    print(f"{Fore.YELLOW}ℹ️  {text}")

def test_health_check(base_url):
    """Test le health check"""
    print_header("TEST 1: Health Check")
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Service is healthy!")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Demand Model: {data.get('demand_model_loaded')}")
            print_info(f"Fraud Model: {data.get('fraud_model_loaded')}")
            print_info(f"Version: {data.get('version')}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False

def test_root_endpoint(base_url):
    """Test l'endpoint racine"""
    print_header("TEST 2: Root Endpoint")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success("Root endpoint accessible!")
            print_info(f"Service: {data.get('service')}")
            print_info(f"Version: {data.get('version')}")
            print_info(f"Docs: {data.get('docs')}")
            return True
        else:
            print_error(f"Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Root endpoint error: {e}")
        return False

def test_demand_prediction(base_url):
    """Test la prédiction de demande"""
    print_header("TEST 3: Demand Prediction")
    
    # Données de test
    today = datetime.now()
    history = [
        {
            "date": (today - timedelta(days=30)).strftime("%Y-%m-%d"),
            "product_id": "test-001",
            "product_name": "Test Product",
            "quantity": 100.0,
            "price": 50.0
        },
        {
            "date": (today - timedelta(days=20)).strftime("%Y-%m-%d"),
            "product_id": "test-001",
            "product_name": "Test Product",
            "quantity": 120.0,
            "price": 50.0
        },
        {
            "date": (today - timedelta(days=10)).strftime("%Y-%m-%d"),
            "product_id": "test-001",
            "product_name": "Test Product",
            "quantity": 110.0,
            "price": 50.0
        }
    ]
    
    payload = {
        "product_id": "test-001",
        "history": history,
        "prediction_days": 30
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/predict/demand",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print_success("Demand prediction successful!")
            print_info(f"Product: {data.get('product_name')}")
            print_info(f"Predicted Quantity: {data.get('predicted_quantity'):.2f}")
            print_info(f"Confidence: {data.get('confidence'):.1%}")
            print_info(f"Days Until Order: {data.get('days_until_order')}")
            print_info(f"Urgency: {data.get('urgency_level')}")
            return True
        else:
            print_error(f"Prediction failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Prediction error: {e}")
        return False

def test_fraud_detection(base_url):
    """Test la détection de fraude"""
    print_header("TEST 4: Fraud Detection")
    
    payload = {
        "amount": 1500.0,
        "transaction_type": "purchase",
        "merchant_category": "electronics",
        "hour_of_day": 14,
        "day_of_week": 2,
        "is_international": False,
        "device_type": "mobile"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/predict/fraud",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print_success("Fraud detection successful!")
            print_info(f"Is Fraud: {data.get('is_fraud')}")
            print_info(f"Fraud Score: {data.get('fraud_score'):.3f}")
            print_info(f"Risk Level: {data.get('risk_level')}")
            print_info(f"Action: {data.get('action')}")
            return True
        else:
            print_error(f"Fraud detection failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Fraud detection error: {e}")
        return False

def test_documentation(base_url):
    """Test l'accès à la documentation"""
    print_header("TEST 5: API Documentation")
    try:
        response = requests.get(f"{base_url}/api/v1/docs", timeout=10)
        if response.status_code == 200:
            print_success("Documentation accessible!")
            print_info(f"URL: {base_url}/api/v1/docs")
            return True
        else:
            print_error(f"Documentation not accessible: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Documentation error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print_error("Usage: python test_render_deployment.py <URL>")
        print_info("Example: python test_render_deployment.py https://ml-prediction-service.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}{'🚀 RENDER DEPLOYMENT TEST SUITE':^60}")
    print(f"{Fore.MAGENTA}{'='*60}")
    print(f"\n{Fore.WHITE}Testing service at: {Fore.CYAN}{base_url}\n")
    
    results = []
    
    # Exécuter tous les tests
    results.append(("Health Check", test_health_check(base_url)))
    results.append(("Root Endpoint", test_root_endpoint(base_url)))
    results.append(("Demand Prediction", test_demand_prediction(base_url)))
    results.append(("Fraud Detection", test_fraud_detection(base_url)))
    results.append(("Documentation", test_documentation(base_url)))
    
    # Résumé
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Fore.GREEN}✅ PASSED" if result else f"{Fore.RED}❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print(f"\n{Fore.CYAN}{'─'*60}")
    if passed == total:
        print(f"{Fore.GREEN}🎉 ALL TESTS PASSED! ({passed}/{total})")
        print(f"{Fore.GREEN}Your ML service is fully operational on Render!")
    else:
        print(f"{Fore.YELLOW}⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
        print(f"{Fore.YELLOW}Check the errors above for details.")
    print(f"{Fore.CYAN}{'─'*60}\n")
    
    # URLs utiles
    print(f"{Fore.MAGENTA}📚 Useful URLs:")
    print(f"{Fore.WHITE}   • API Docs:  {Fore.CYAN}{base_url}/api/v1/docs")
    print(f"{Fore.WHITE}   • Health:    {Fore.CYAN}{base_url}/api/v1/health")
    print(f"{Fore.WHITE}   • Root:      {Fore.CYAN}{base_url}\n")

if __name__ == "__main__":
    main()
