#!/usr/bin/env python3
"""
Test dengan conversation lengkap untuk melihat date parsing dengan commitment kuat
"""

import requests
import json

def test_full_conversation_with_dates():
    """Test dengan conversation lengkap yang mengandung date expressions"""
    
    print("🗓️ Testing Full Conversation with Date Parsing")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    endpoint = "/api/v1/endpoints/conversation/predict"
    
    test_case = {
        "topic": "telecollection",
        "customer_id": "ICON12345",
        "conversation": [
            {"q": "Status dihubungi?", "a": "Terhubung"},
            {"q": "Apakah Anda sudah mengetahui tagihan bulan ini?", "a": "Ya, saya tahu ada tagihan"},
            {"q": "Berapa tagihan yang harus Anda bayar?", "a": "Sekitar 350 ribu"},
            {"q": "Kapan Anda berencana melakukan pembayaran?", "a": "Besok pasti saya bayar"},
            {"q": "Apakah ada kendala dalam pembayaran?", "a": "Tidak ada kendala"},
            {"q": "Metode pembayaran apa yang akan Anda gunakan?", "a": "Transfer ATM"}
        ]
    }
    
    try:
        print(f"📡 Calling: {base_url}{endpoint}")
        print(f"📝 Customer Answer: 'Besok pasti saya bayar'")
        
        response = requests.post(
            f"{base_url}{endpoint}",
            json=test_case,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            prediction = result.get("result", {})
            
            print(f"\n✅ Success! Prediction Results:")
            print(f"   📋 Status: {prediction.get('status', 'N/A')}")
            print(f"   🎯 Keputusan: {prediction.get('keputusan', 'N/A')}")
            print(f"   💰 Estimasi Pembayaran: {prediction.get('estimasi_pembayaran', 'N/A')}")
            print(f"   🎪 Confidence: {prediction.get('confidence', 'N/A')}")
            print(f"   📈 Probability: {prediction.get('probability', 'N/A')}")
            print(f"   📝 Alasan: {prediction.get('alasan', 'N/A')}")
            
            # Check for detailed analysis
            if 'detail_analysis' in prediction:
                detail = prediction['detail_analysis']
                timeline_commitments = detail.get('timeline_commitments', [])
                if timeline_commitments:
                    print(f"\n📅 TIMELINE COMMITMENTS ANALYSIS:")
                    for i, commitment in enumerate(timeline_commitments, 1):
                        print(f"   {i}. Answer: '{commitment.get('answer', '')[:30]}...'")
                        print(f"      Strength: {commitment.get('strength', 0)}")
                        
                        time_info = commitment.get('time_parsed', {})
                        if time_info:
                            print(f"      🗓️ Parsed Time Info:")
                            print(f"         • Detected: '{time_info.get('detected_timeframe', 'N/A')}'")
                            print(f"         • Date: {time_info.get('formatted_date', 'N/A')}")
                            print(f"         • Confidence: {time_info.get('confidence', 0)}%")
                        print()
                else:
                    print(f"\n⚠️ No timeline commitments found")
            
            # Expected result untuk 'besok'
            print(f"\n🎯 EXPECTED vs ACTUAL:")
            print(f"   Expected Date: 16 Oktober 2025")
            actual_estimasi = prediction.get('estimasi_pembayaran', 'N/A')
            if '16 Oktober 2025' in actual_estimasi:
                print(f"   ✅ Date parsing SUCCESS!")
            else:
                print(f"   ❌ Date parsing not reflected in estimasi")
                print(f"   Actual: {actual_estimasi}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_full_conversation_with_dates()