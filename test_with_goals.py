#!/usr/bin/env python3
"""
Test dengan goal yang benar untuk setiap conversation entry
"""

import requests
import json

def test_with_correct_goals():
    """Test dengan field goal yang benar"""
    
    print("🗓️ Testing with Correct Goal Context")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    endpoint = "/api/v1/endpoints/conversation/predict"
    
    test_case = {
        "topic": "telecollection",
        "customer_id": "ICON12345", 
        "conversation": [
            {"q": "Status dihubungi?", "a": "Terhubung", "goal": "status_contact"},
            {"q": "Apakah Anda sudah mengetahui tagihan bulan ini?", "a": "Ya, saya tahu ada tagihan", "goal": "payment_awareness"},
            {"q": "Berapa tagihan yang harus Anda bayar?", "a": "Sekitar 350 ribu", "goal": "payment_amount"},
            {"q": "Kapan Anda berencana melakukan pembayaran?", "a": "Besok pasti saya bayar", "goal": "payment_timeline"},
            {"q": "Apakah ada kendala dalam pembayaran?", "a": "Tidak ada kendala", "goal": "payment_barrier"},
            {"q": "Metode pembayaran apa yang akan Anda gunakan?", "a": "Transfer ATM", "goal": "payment_method"}
        ]
    }
    
    try:
        print(f"📡 Calling: {base_url}{endpoint}")
        print(f"📝 Key Answer: 'Besok pasti saya bayar' with goal: 'payment_timeline'")
        
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
            
            print(f"\n✅ Success! Results:")
            print(f"   📋 Status: {prediction.get('status', 'N/A')}")
            print(f"   🎯 Keputusan: {prediction.get('keputusan', 'N/A')}")
            print(f"   💰 Estimasi Pembayaran: {prediction.get('estimasi_pembayaran', 'N/A')}")
            print(f"   📈 Probability: {prediction.get('probability', 'N/A')}")
            print(f"   📝 Alasan: {prediction.get('alasan', 'N/A')}")
            
            # Check timeline commitments
            if 'detail_analysis' in prediction:
                detail = prediction['detail_analysis']
                timeline_commitments = detail.get('timeline_commitments', [])
                if timeline_commitments:
                    print(f"\n📅 Timeline Commitments Found: {len(timeline_commitments)}")
                    for i, commitment in enumerate(timeline_commitments, 1):
                        time_info = commitment.get('time_parsed', {})
                        if time_info and time_info.get('formatted_date'):
                            print(f"   {i}. Date: {time_info.get('formatted_date', '')}")
                            print(f"      From: '{time_info.get('detected_timeframe', '')}'")
                            print(f"      Confidence: {time_info.get('confidence', 0)}%")
                
                # Check if date is reflected in estimasi
                estimasi = prediction.get('estimasi_pembayaran', '')
                if '16 Oktober 2025' in estimasi:
                    print(f"\n🎉 SUCCESS: Date parsing reflected in Estimasi Pembayaran!")
                else:
                    print(f"\n⚠️ Date not yet reflected in Estimasi Pembayaran")
                    print(f"   Timeline commitments exist but not used in estimation")
                    
            else:
                print(f"\n❌ No detail_analysis found")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_with_correct_goals()