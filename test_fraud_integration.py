#!/usr/bin/env python3
"""
Test script for fraud detection integration
Run this to verify the ML fraud detection service is working correctly
"""

import requests
import json
from datetime import datetime

ML_SERVICE_URL = "http://localhost:8000"

def test_health():
    """Test if ML service is running"""
    print("🔍 Testing ML service health...")
    try:
        response = requests.get(f"{ML_SERVICE_URL}/api/v1/health")
        data = response.json()
        print(f"✅ ML Service Status: {data['status']}")
        print(f"   Fraud Model Loaded: {data['fraud_model_loaded']}")
        print(f"   Version: {data['version']}")
        return True
    except Exception as e:
        print(f"❌ ML Service unreachable: {e}")
        return False

def test_fraud_prediction(test_case):
    """Test fraud prediction with a specific case"""
    print(f"\n🧪 Testing: {test_case['name']}")
    print(f"   Amount: {test_case['amount']}, Hour: {test_case['hour']}, Night: {test_case['is_night']}")
    
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/api/v1/predict/fraud",
            json=test_case['data'],
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Fraud Score: {result['fraud_score']:.2%}")
            print(f"   Is Fraud: {result['is_fraud']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Action: {result['action']}")
            return result
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return None

def main():
    print("=" * 60)
    print("🚀 Fraud Detection Integration Test")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ ML service is not running. Start it with:")
        print("   cd PI-DEV-ML")
        print("   uvicorn app.main:app --reload")
        return
    
    # Test cases
    test_cases = [
        {
            "name": "Low Risk - Normal transaction",
            "data": {
                "amount": 500.0,
                "transaction_type": "ENCAISSEMENT",
                "hour": 14,
                "is_weekend": 0,
                "is_night": 0,
                "velocity_score": 0.1,
                "geo_anomaly_score": 0.1,
                "spending_deviation_score": 0.1
            }
        },
        {
            "name": "Medium Risk - High amount during day",
            "data": {
                "amount": 8000.0,
                "transaction_type": "DECAISSEMENT",
                "hour": 15,
                "is_weekend": 0,
                "is_night": 0,
                "velocity_score": 0.3,
                "geo_anomaly_score": 0.2,
                "spending_deviation_score": 0.4
            }
        },
        {
            "name": "High Risk - Large amount at night",
            "data": {
                "amount": 15000.0,
                "transaction_type": "DECAISSEMENT",
                "hour": 23,
                "is_weekend": 1,
                "is_night": 1,
                "velocity_score": 0.8,
                "geo_anomaly_score": 0.7,
                "spending_deviation_score": 0.9
            }
        },
        {
            "name": "High Risk - Very large amount",
            "data": {
                "amount": 25000.0,
                "transaction_type": "DECAISSEMENT",
                "hour": 2,
                "is_weekend": 0,
                "is_night": 1,
                "velocity_score": 0.6,
                "geo_anomaly_score": 0.5,
                "spending_deviation_score": 0.7
            }
        }
    ]
    
    # Run tests
    results = []
    for test_case in test_cases:
        result = test_fraud_prediction(test_case)
        if result:
            results.append({
                "name": test_case["name"],
                "score": result["fraud_score"],
                "action": result["action"]
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    if results:
        for r in results:
            emoji = "🚨" if r["action"] == "block" else "⚠️" if r["action"] == "flag" else "✅"
            print(f"{emoji} {r['name']}")
            print(f"   Score: {r['score']:.2%} | Action: {r['action'].upper()}")
        
        print(f"\n✅ All {len(results)} tests completed successfully!")
    else:
        print("❌ No tests completed successfully")
    
    print("\n💡 Next steps:")
    print("   1. Start the backend: cd PI-DEV-BACKEND && npm run start:dev")
    print("   2. Start the frontend: cd PI-DEV-FRONT && npm run dev")
    print("   3. Create a transaction and check the fraud detection")
    print("=" * 60)

if __name__ == "__main__":
    main()
