#!/usr/bin/env python3
"""
Test endpoint /predict untuk melihat apakah date parsing berfungsi di frontend
"""

import requests
import json

def test_prediction_endpoint_with_dates():
    """Test endpoint dengan data yang mengandung kata waktu"""
    
    print("🧪 Testing /predict endpoint dengan kata waktu")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test cases dengan kata waktu
    test_cases = [
        {
            "name": "Customer bilang 'besok bayar'",
            "data": {
                "topic": "telecollection",
                "customer_id": "ICON12345",
                "conversation": [
                    {"q": "Status dihubungi?", "a": "Terhubung"},
                    {"q": "Kapan Anda berencana melakukan pembayaran?", "a": "Besok saya bayar kok"}
                ]
            }
        },
        {
            "name": "Customer bilang '3 hari lagi'",
            "data": {
                "topic": "telecollection",
                "customer_id": "ICON67890",
                "conversation": [
                    {"q": "Status dihubungi?", "a": "Terhubung"},
                    {"q": "Kapan Anda berencana melakukan pembayaran?", "a": "3 hari lagi saya transfer"}
                ]
            }
        },
        {
            "name": "Customer bilang 'senin ke bank'",
            "data": {
                "topic": "telecollection",
                "customer_id": "ICON11111",
                "conversation": [
                    {"q": "Status dihubungi?", "a": "Terhubung"},
                    {"q": "Kapan Anda berencana melakukan pembayaran?", "a": "Senin saya ke bank dulu"}
                ]
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/conversations/predict",
                json=test_case["data"],
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                prediction = result.get("result", {})
                
                print(f"✅ Status: {response.status_code}")
                print(f"📊 Response fields:")
                
                # Key frontend fields
                key_fields = [
                    "status", "estimasi_pembayaran", "alasan", 
                    "keputusan", "confidence", "probability"
                ]
                
                for field in key_fields:
                    value = prediction.get(field, "NOT_SET")
                    if field == "estimasi_pembayaran":
                        print(f"   🎯 {field}: {value}")  # Highlight this one
                    else:
                        print(f"   • {field}: {value}")
                
                # Check enhanced fields
                if "detail_analysis" in prediction:
                    detail = prediction["detail_analysis"]
                    timeline_commitments = detail.get("timeline_commitments", [])
                    if timeline_commitments:
                        print(f"   📅 Timeline Commitments Found: {len(timeline_commitments)}")
                        for j, commitment in enumerate(timeline_commitments):
                            time_info = commitment.get("time_parsed", {})
                            if time_info and time_info.get("formatted_date"):
                                print(f"      {j+1}. '{time_info.get('detected_timeframe', '')}' → {time_info.get('formatted_date', '')}")
                
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed - Server not running?")
        except Exception as e:
            print(f"❌ Error: {e}")
            
        print("-" * 50)

if __name__ == "__main__":
    test_prediction_endpoint_with_dates()