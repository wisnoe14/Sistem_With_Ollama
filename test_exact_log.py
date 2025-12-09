#!/usr/bin/env python3
"""
Test exact conversation dari log untuk memastikan 'Besok' dikenali
"""

import requests
import json

def test_exact_conversation():
    """Test conversation persis seperti di log"""
    
    print("🗓️ Testing Exact Conversation from Log")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    endpoint = "/api/v1/endpoints/conversation/predict"
    
    # Conversation persis dari log  
    test_data = {
        "topic": "telecollection",
        "customer_id": "ICON12345",
        "conversation": [
            {"q": "Status Dihubungi?", "a": "Dihubungi"},
            {"q": "Halo Budi, selamat pagi! Saya Wisnu dari ICONNET. Gimana kabarnya hari ini? Oh iya, saya mau tanya nih, untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?", "a": "Belum bayar"},
            {"q": "Saya ingin memahami situasinya - ada kendala khusus yang membuat pembayaran tertunda?", "a": "Belum gajian"},
            {"q": "Kira-kira kapan Bapak/Ibu bisa melakukan pembayaran? Supaya kita bisa bantu arrange jadwalnya", "a": "Besok"}
        ]
    }
    
    try:
        print(f"📡 Calling: {base_url}{endpoint}")
        print(f"📝 Key Answer: 'Besok' (should now be timeline_commitment)")
        
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
            
            print(f"\n✅ Results:")
            print(f"   🎯 Keputusan: {prediction.get('keputusan', 'N/A')}")
            print(f"   💰 Estimasi Pembayaran: {prediction.get('estimasi_pembayaran', 'N/A')}")
            print(f"   📈 Probability: {prediction.get('probability', 'N/A')}")
            print(f"   📝 Alasan: {prediction.get('alasan', 'N/A')}")
            
            # Check if improvement happened
            estimasi = prediction.get('estimasi_pembayaran', '')
            if 'Follow-up Khusus' in estimasi:
                print(f"\n⚠️ Still showing generic follow-up")
                print(f"   Need to check timeline commitments in detail_analysis")
            elif '16 Oktober 2025' in estimasi:
                print(f"\n🎉 SUCCESS: Date parsing now working!")
            else:
                print(f"\n🔍 Different result: {estimasi}")
            
            # Show detail analysis if available
            if 'detail_analysis' in prediction:
                detail = prediction['detail_analysis']
                timeline_commitments = detail.get('timeline_commitments', [])
                barriers = detail.get('barriers', [])
                
                print(f"\n📊 Analysis Details:")
                print(f"   • Timeline Commitments: {len(timeline_commitments)}")
                print(f"   • Barriers: {len(barriers)}")
                
                if timeline_commitments:
                    for i, commitment in enumerate(timeline_commitments, 1):
                        time_info = commitment.get('time_parsed', {})
                        if time_info and time_info.get('formatted_date'):
                            print(f"   📅 Commitment {i}: '{time_info.get('detected_timeframe', '')}' → {time_info.get('formatted_date', '')}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_exact_conversation()