#!/usr/bin/env python3
"""
Test endpoint dengan conversation yang lebih kuat untuk melihat date parsing
"""

import requests
import json

def test_strong_commitment():
    """Test dengan commitment yang kuat untuk melihat date parsing"""
    
    print("🗓️ Testing Date Parsing in Strong Commitment")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    endpoint = "/api/v1/endpoints/conversation/predict"
    
    test_data = {
        "topic": "telecollection",
        "customer_id": "ICON12345",
        "conversation": [
            {"q": "Status dihubungi?", "a": "Terhubung"},
            {"q": "Apakah Anda sudah mengetahui tagihan bulan ini?", "a": "Ya, saya tahu ada tagihan 300 ribu"},
            {"q": "Kapan Anda berencana melakukan pembayaran?", "a": "Besok pasti saya bayar"},
            {"q": "Apakah ada kendala dalam pembayaran?", "a": "Tidak ada kendala, sudah siap"},
            {"q": "Metode pembayaran apa yang akan Anda gunakan?", "a": "Transfer bank langsung"}
        ]
    }
    
    try:
        print(f"📡 Calling: {base_url}{endpoint}")
        
        response = requests.post(
            f"{base_url}{endpoint}",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            prediction = result.get("result", {})
            
            print(f"✅ Success!")
            print(f"📋 Prediction Results:")
            print(f"   • Status: {prediction.get('status', 'N/A')}")
            print(f"   • Keputusan: {prediction.get('keputusan', 'N/A')}")
            print(f"   🎯 Estimasi Pembayaran: {prediction.get('estimasi_pembayaran', 'N/A')}")
            print(f"   • Confidence: {prediction.get('confidence', 'N/A')}")
            print(f"   • Probability: {prediction.get('probability', 'N/A')}")
            print(f"   📝 Alasan: {prediction.get('alasan', 'N/A')}")
            
            # Check for timeline commitments with date info
            if 'detail_analysis' in prediction:
                detail = prediction['detail_analysis']
                timeline_commitments = detail.get('timeline_commitments', [])
                if timeline_commitments:
                    print(f"\n📅 Timeline Commitments Found: {len(timeline_commitments)}")
                    for i, commitment in enumerate(timeline_commitments):
                        time_info = commitment.get('time_parsed', {})
                        if time_info and time_info.get('formatted_date'):
                            print(f"   {i+1}. '{time_info.get('detected_timeframe', '')}' → {time_info.get('formatted_date', '')}")
                            print(f"      Confidence: {time_info.get('confidence', 0)}%")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_strong_commitment()