"""
Test script untuk memverifikasi risk indicator di API response
"""
import requests
import json

API_BASE = "http://localhost:8000/api/v1/endpoints"

# Test case 1: Telecollection dengan pembayaran selesai (should be low risk - green)
test_1 = {
    "customer_id": "TEST001",
    "topic": "telecollection",
    "conversation": [
        {"q": "Status pembayaran?", "a": "Sudah bayar kemarin"},
        {"q": "Kapan bayar?", "a": "Kemarin sore sudah transfer"}
    ]
}

# Test case 2: Retention dengan pindah rumah (should be high risk - red)
test_2 = {
    "customer_id": "TEST002",
    "topic": "retention",
    "conversation": [
        {"q": "Perkenalkan saya dari ICONNET", "a": "Ya, benar"},
        {"q": "Apakah berminat aktivasi kembali?", "a": "Tidak, saya mau berhenti karena pindah rumah"}
    ]
}

# Test case 3: Winback dengan pertimbangan (should be medium risk - yellow)
test_3 = {
    "customer_id": "TEST003",
    "topic": "winback",
    "conversation": [
        {"q": "Perkenalkan saya dari ICONNET", "a": "Ya"},
        {"q": "Ada promo comeback", "a": "Saya pertimbangkan dulu"}
    ]
}

print("=" * 80)
print("TESTING RISK INDICATOR IN API RESPONSES")
print("=" * 80)

for i, test_case in enumerate([test_1, test_2, test_3], 1):
    print(f"\n📊 Test Case {i}: {test_case['topic'].upper()}")
    print("-" * 80)
    
    try:
        response = requests.post(
            f"{API_BASE}/conversation/predict",
            json=test_case,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            prediction = result.get("result", {})
            
            print(f"✅ Status: {response.status_code}")
            print(f"📋 Keputusan: {prediction.get('keputusan', 'N/A')}")
            print(f"📝 Status: {prediction.get('status', 'N/A')}")
            
            # Check risk indicator fields
            if 'risk_level' in prediction:
                print(f"\n🎯 RISK INDICATOR FOUND:")
                print(f"   • Risk Level: {prediction.get('risk_level')}")
                print(f"   • Risk Label: {prediction.get('risk_label')}")
                print(f"   • Risk Color: {prediction.get('risk_color')}")
                print(f"   • Signals: {prediction.get('signals', [])}")
            else:
                print(f"\n⚠️  WARNING: Risk indicator fields NOT found in response!")
                print(f"   Available keys: {list(prediction.keys())}")
            
            print(f"\n💡 Alasan: {prediction.get('alasan', 'N/A')[:100]}...")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

print("\n" + "=" * 80)
print("TEST COMPLETED")
print("=" * 80)
