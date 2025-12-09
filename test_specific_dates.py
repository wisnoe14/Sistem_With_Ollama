#!/usr/bin/env python3
"""
Test specific time expressions untuk melihat date parsing
"""

import requests
import json

def test_specific_dates():
    """Test dengan kata waktu spesifik"""
    
    print("🗓️ Testing Specific Time Expressions")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    endpoint = "/api/v1/endpoints/conversation/predict"
    
    test_cases = [
        {
            "name": "Customer bilang 'besok'",
            "conversation": [
                {"q": "Status dihubungi?", "a": "Terhubung"},
                {"q": "Kapan Anda berencana melakukan pembayaran?", "a": "Besok saya bayar"}
            ]
        },
        {
            "name": "Customer bilang '3 hari lagi'",
            "conversation": [
                {"q": "Status dihubungi?", "a": "Terhubung"},
                {"q": "Kapan Anda berencana melakukan pembayaran?", "a": "3 hari lagi saya transfer"}
            ]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        
        test_data = {
            "topic": "telecollection",
            "customer_id": f"ICON{12340 + i}",
            "conversation": test_case["conversation"]
        }
        
        try:
            response = requests.post(
                f"{base_url}{endpoint}",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                prediction = result.get("result", {})
                
                print(f"   📊 Keputusan: {prediction.get('keputusan', 'N/A')}")
                print(f"   🎯 Estimasi Pembayaran: {prediction.get('estimasi_pembayaran', 'N/A')}")
                
                # Check for timeline commitments
                if 'detail_analysis' in prediction:
                    detail = prediction['detail_analysis']
                    timeline_commitments = detail.get('timeline_commitments', [])
                    if timeline_commitments:
                        print(f"   📅 Date Parsing Results:")
                        for j, commitment in enumerate(timeline_commitments):
                            time_info = commitment.get('time_parsed', {})
                            if time_info and time_info.get('formatted_date'):
                                print(f"      • '{time_info.get('detected_timeframe', '')}' → {time_info.get('formatted_date', '')}")
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_specific_dates()