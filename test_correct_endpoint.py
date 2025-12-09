#!/usr/bin/env python3
"""
Quick test untuk endpoint /predict yang benar
"""

import requests
import json

def test_correct_endpoint():
    """Test endpoint yang benar"""
    
    print("🧪 Testing Correct Endpoint")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    endpoint = "/api/v1/endpoints/conversation/predict"
    
    test_data = {
        "topic": "telecollection",
        "customer_id": "ICON12345",
        "conversation": [
            {"q": "Status dihubungi?", "a": "Terhubung"},
            {"q": "Kapan Anda berencana melakukan pembayaran?", "a": "Besok saya bayar"}
        ]
    }
    
    try:
        print(f"📡 Calling: {base_url}{endpoint}")
        
        response = requests.post(
            f"{base_url}{endpoint}",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            prediction = result.get("result", {})
            
            print(f"✅ Success!")
            print(f"📋 Key fields:")
            print(f"   • Status: {prediction.get('status', 'N/A')}")
            print(f"   • Keputusan: {prediction.get('keputusan', 'N/A')}")
            print(f"   🎯 Estimasi Pembayaran: {prediction.get('estimasi_pembayaran', 'N/A')}")
            print(f"   • Alasan: {prediction.get('alasan', 'N/A')[:50]}...")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed - Server not running?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_correct_endpoint()