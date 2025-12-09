#!/usr/bin/env python3
"""
🧪 TEST WINBACK PREDICTION FIX
Testing the fixed winback prediction system with enhanced frontend format
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.services.gpt_service import generate_final_prediction

def test_winback_prediction():
    """Test winback prediction with various scenarios"""
    
    # Test Case 1: Customer agrees to reactivation
    print("="*60)
    print("🧪 TEST CASE 1: Customer Agrees to Reactivation")
    print("="*60)
    
    winback_conversation_positive = [
        {"q": "Status Dihubungi?", "a": "Dihubungi"},
        {"q": "Selamat sore, Bapak/Ibu. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Budi?", "a": "Ya, benar"},
        {"q": "Sebagai bentuk apresiasi, kami menawarkan promo gratis 1 bulan untuk Bapak/Ibu jika bersedia mengaktifkan layanan ICONNET kembali. Promo ini bisa Bapak/Ibu dapatkan dengan cara melakukan 1x pembayaran untuk mengaktifkan layanan ICONNETnya. Apakah Bapak/Ibu bersedia untuk mengaktifkan layanan ICONNETnya kembali?", "a": "Ya, bersedia"},
        {"q": "Baik Bapak/Ibu, akan kami bantu untuk mengirimkan kode pembayaran melalui email. Untuk estimasi pembayaran akan dibayarkan berapa jam ke depan ya?", "a": "Hari ini juga"},
        {"q": "Baik Bapak/Ibu, untuk perangkat ICONNET-nya apakah masih berada di lokasi rumah?", "a": "Masih ada"}
    ]
    
    try:
        result = generate_final_prediction("winback", winback_conversation_positive)
        print(f"✅ PREDICTION RESULT:")
        print(f"   Keputusan: {result.get('keputusan')}")
        print(f"   Probability: {result.get('probability')}%")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   Alasan: {result.get('alasan')}")
        print(f"   Tanggal Prediksi: {result.get('tanggal_prediksi')}")
        
        detail_analysis = result.get('detail_analysis', {})
        print(f"\n📊 DETAIL ANALYSIS:")
        print(f"   Interest Score: {detail_analysis.get('interest_score')}")
        print(f"   Commitment Score: {detail_analysis.get('commitment_score')}")
        print(f"   Cooperation Rate: {detail_analysis.get('cooperation_rate')}")
        print(f"   Objection Count: {detail_analysis.get('objection_count')}")
        print(f"   Price Sensitivity: {detail_analysis.get('price_sensitivity')}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("🧪 TEST CASE 2: Customer Rejects Due to Service Issues")
    print("="*60)
    
    # Test Case 2: Customer rejects due to service issues
    winback_conversation_negative = [
        {"q": "Status Dihubungi?", "a": "Dihubungi"},
        {"q": "Selamat sore, Bapak/Ibu. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Budi?", "a": "Ya, benar"},
        {"q": "Sebagai bentuk apresiasi, kami menawarkan promo gratis 1 bulan untuk Bapak/Ibu jika bersedia mengaktifkan layanan ICONNET kembali. Promo ini bisa Bapak/Ibu dapatkan dengan cara melakukan 1x pembayaran untuk mengaktifkan layanan ICONNETnya. Apakah Bapak/Ibu bersedia untuk mengaktifkan layanan ICONNETnya kembali?", "a": "Tidak, terima kasih"},
        {"q": "Baik Bapak/Ibu, jika boleh tahu karena apa ya tidak bersedia mengaktifkan kembali layanan ICONNET?", "a": "Ada keluhan layanan"},
        {"q": "Terima kasih, Bapak/Ibu. Kami melihat bahwa layanan ICONNET Bapak/Ibu sedang terputus, dan kami ingin tahu apakah ada kendala yang bisa kami bantu? Saat ini kami sedang memiliki promo menarik untuk Bapak/Ibu. Apakah boleh saya sampaikan lebih lanjut?", "a": "Tidak tertarik"},
        {"q": "Baik Bapak/Ibu, untuk perangkat ICONNET-nya apakah masih berada di lokasi rumah?", "a": "Sudah dikembalikan"}
    ]
    
    try:
        result = generate_final_prediction("winback", winback_conversation_negative)
        print(f"✅ PREDICTION RESULT:")
        print(f"   Keputusan: {result.get('keputusan')}")
        print(f"   Probability: {result.get('probability')}%")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   Alasan: {result.get('alasan')}")
        print(f"   Tanggal Prediksi: {result.get('tanggal_prediksi')}")
        
        detail_analysis = result.get('detail_analysis', {})
        print(f"\n📊 DETAIL ANALYSIS:")
        print(f"   Interest Score: {detail_analysis.get('interest_score')}")
        print(f"   Commitment Score: {detail_analysis.get('commitment_score')}")
        print(f"   Cooperation Rate: {detail_analysis.get('cooperation_rate')}")
        print(f"   Objection Count: {detail_analysis.get('objection_count')}")
        print(f"   Price Sensitivity: {detail_analysis.get('price_sensitivity')}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("🧪 TEST CASE 3: Empty Conversation")
    print("="*60)
    
    # Test Case 3: Empty conversation
    try:
        result = generate_final_prediction("winback", [])
        print(f"✅ PREDICTION RESULT:")
        print(f"   Keputusan: {result.get('keputusan')}")
        print(f"   Probability: {result.get('probability')}%")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   Alasan: {result.get('alasan')}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_winback_prediction()