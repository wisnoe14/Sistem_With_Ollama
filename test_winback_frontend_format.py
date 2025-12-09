#!/usr/bin/env python3
"""
🧪 TEST FRONTEND FORMAT FOR WINBACK PREDICTION
Testing the enhanced frontend format for winback predictions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from datetime import datetime

# API endpoint for prediction
API_URL = "http://localhost:8000/api/v1/endpoints/conversation/predict"

def test_winback_frontend_format():
    """Test winback prediction with frontend format conversion"""
    
    print("="*80)
    print("🎯 TESTING WINBACK PREDICTION - FRONTEND FORMAT")
    print("="*80)
    
    # Test Case 1: Successful reactivation scenario
    test_conversation_1 = [
        {"q": "Status Dihubungi?", "a": "Dihubungi"},
        {"q": "Selamat sore, Bapak/Ibu. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Budi?", "a": "Ya, benar"},
        {"q": "Sebagai bentuk apresiasi, kami menawarkan promo gratis 1 bulan untuk Bapak/Ibu jika bersedia mengaktifkan layanan ICONNET kembali. Promo ini bisa Bapak/Ibu dapatkan dengan cara melakukan 1x pembayaran untuk mengaktifkan layanan ICONNETnya. Apakah Bapak/Ibu bersedia untuk mengaktifkan layanan ICONNETnya kembali?", "a": "Ya, bersedia"},
        {"q": "Baik Bapak/Ibu, akan kami bantu untuk mengirimkan kode pembayaran melalui email. Untuk estimasi pembayaran akan dibayarkan berapa jam ke depan ya?", "a": "Hari ini juga"},
        {"q": "Baik Bapak/Ibu, untuk perangkat ICONNET-nya apakah masih berada di lokasi rumah?", "a": "Masih ada"}
    ]
    
    payload_1 = {
        "customer_id": "ICON12345",
        "topic": "winback", 
        "conversation": test_conversation_1
    }
    
    try:
        print("📤 SENDING REQUEST - Test Case 1: Customer Agrees")
        print("="*60)
        response = requests.post(API_URL, json=payload_1, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            prediction_result = result.get("result", {})
            
            print("✅ RESPONSE RECEIVED:")
            print(f"   Customer ID: {prediction_result.get('customer_id')}")
            print(f"   Topic: {prediction_result.get('topic')}")
            print(f"   Status Dihubungi: {prediction_result.get('status_dihubungi')}")
            print(f"   Status: {prediction_result.get('status')}")
            print(f"   Keputusan: {prediction_result.get('keputusan')}")
            print(f"   Probability: {prediction_result.get('probability')}")
            print(f"   Confidence: {prediction_result.get('confidence')}")
            print(f"   Alasan: {prediction_result.get('alasan')}")
            
            print("\n🎯 WINBACK-SPECIFIC FIELDS:")
            print(f"   Minat Berlangganan: {prediction_result.get('minat_berlangganan')}")
            print(f"   Jenis Promo: {prediction_result.get('jenis_promo')}")
            print(f"   Estimasi Pembayaran: {prediction_result.get('estimasi_pembayaran')}")
            print(f"   Equipment Status: {prediction_result.get('equipment_status')}")
            print(f"   Service Issues: {prediction_result.get('service_issues')}")
            
            print("\n📊 ENHANCED PREDICTION FIELDS:")
            print(f"   Probability Score: {prediction_result.get('probability_score')}")
            print(f"   Confidence Level: {prediction_result.get('confidence_level')}")
            print(f"   Tanggal Prediksi: {prediction_result.get('tanggal_prediksi')}")
            
        else:
            print(f"❌ API ERROR: Status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("🧪 TEST CASE 2: Customer Rejection Due to Service Issues")
    print("="*80)
    
    # Test Case 2: Customer rejects due to service issues
    test_conversation_2 = [
        {"q": "Status Dihubungi?", "a": "Dihubungi"},
        {"q": "Selamat sore, Bapak/Ibu. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Budi?", "a": "Ya, benar"},
        {"q": "Sebagai bentuk apresiasi, kami menawarkan promo gratis 1 bulan untuk Bapak/Ibu jika bersedia mengaktifkan layanan ICONNET kembali. Promo ini bisa Bapak/Ibu dapatkan dengan cara melakukan 1x pembayaran untuk mengaktifkan layanan ICONNETnya. Apakah Bapak/Ibu bersedia untuk mengaktifkan layanan ICONNETnya kembali?", "a": "Tidak, terima kasih"},
        {"q": "Baik Bapak/Ibu, jika boleh tahu karena apa ya tidak bersedia mengaktifkan kembali layanan ICONNET?", "a": "Ada keluhan layanan sebelumnya"},
        {"q": "Terima kasih, Bapak/Ibu. Kami melihat bahwa layanan ICONNET Bapak/Ibu sedang terputus, dan kami ingin tahu apakah ada kendala yang bisa kami bantu? Saat ini kami sedang memiliki promo menarik untuk Bapak/Ibu. Apakah boleh saya sampaikan lebih lanjut?", "a": "Tidak tertarik"},
        {"q": "Baik Bapak/Ibu, untuk perangkat ICONNET-nya apakah masih berada di lokasi rumah?", "a": "Sudah dikembalikan"}
    ]
    
    payload_2 = {
        "customer_id": "ICON54321",
        "topic": "winback",
        "conversation": test_conversation_2
    }
    
    try:
        print("📤 SENDING REQUEST - Test Case 2: Customer Rejects")
        print("="*60)
        response = requests.post(API_URL, json=payload_2, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            prediction_result = result.get("result", {})
            
            print("✅ RESPONSE RECEIVED:")
            print(f"   Customer ID: {prediction_result.get('customer_id')}")
            print(f"   Topic: {prediction_result.get('topic')}")
            print(f"   Status Dihubungi: {prediction_result.get('status_dihubungi')}")
            print(f"   Status: {prediction_result.get('status')}")
            print(f"   Keputusan: {prediction_result.get('keputusan')}")
            print(f"   Probability: {prediction_result.get('probability')}")
            print(f"   Confidence: {prediction_result.get('confidence')}")
            print(f"   Alasan: {prediction_result.get('alasan')}")
            
            print("\n🎯 WINBACK-SPECIFIC FIELDS:")
            print(f"   Minat Berlangganan: {prediction_result.get('minat_berlangganan')}")
            print(f"   Jenis Promo: {prediction_result.get('jenis_promo')}")
            print(f"   Estimasi Pembayaran: {prediction_result.get('estimasi_pembayaran')}")
            print(f"   Equipment Status: {prediction_result.get('equipment_status')}")
            print(f"   Service Issues: {prediction_result.get('service_issues')}")
            
        else:
            print(f"❌ API ERROR: Status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)
    print("🧪 TEST CASE 3: Equipment Already Returned")
    print("="*80)
    
    # Test Case 3: Equipment already returned
    test_conversation_3 = [
        {"q": "Status Dihubungi?", "a": "Dihubungi"},
        {"q": "Selamat sore, Bapak/Ibu. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Budi?", "a": "Ya, benar"},
        {"q": "Sebagai bentuk apresiasi, kami menawarkan promo gratis 1 bulan untuk Bapak/Ibu jika bersedia mengaktifkan layanan ICONNET kembali. Promo ini bisa Bapak/Ibu dapatkan dengan cara melakukan 1x pembayaran untuk mengaktifkan layanan ICONNETnya. Apakah Bapak/Ibu bersedia untuk mengaktifkan layanan ICONNETnya kembali?", "a": "Tidak, sudah pindah rumah"},
        {"q": "Baik Bapak/Ibu, untuk perangkat ICONNET-nya apakah masih berada di lokasi rumah?", "a": "Sudah dikembalikan"}
    ]
    
    payload_3 = {
        "customer_id": "ICON99999",
        "topic": "winback",
        "conversation": test_conversation_3
    }
    
    try:
        print("📤 SENDING REQUEST - Test Case 3: Equipment Returned")
        print("="*60)
        response = requests.post(API_URL, json=payload_3, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            prediction_result = result.get("result", {})
            
            print("✅ RESPONSE RECEIVED:")
            print(f"   Customer ID: {prediction_result.get('customer_id')}")
            print(f"   Topic: {prediction_result.get('topic')}")
            print(f"   Status Dihubungi: {prediction_result.get('status_dihubungi')}")
            print(f"   Status: {prediction_result.get('status')}")
            print(f"   Keputusan: {prediction_result.get('keputusan')}")
            print(f"   Probability: {prediction_result.get('probability')}")
            print(f"   Confidence: {prediction_result.get('confidence')}")
            print(f"   Alasan: {prediction_result.get('alasan')}")
            
            print("\n🎯 WINBACK-SPECIFIC FIELDS:")
            print(f"   Minat Berlangganan: {prediction_result.get('minat_berlangganan')}")
            print(f"   Jenis Promo: {prediction_result.get('jenis_promo')}")
            print(f"   Estimasi Pembayaran: {prediction_result.get('estimasi_pembayaran')}")
            print(f"   Equipment Status: {prediction_result.get('equipment_status')}")
            print(f"   Service Issues: {prediction_result.get('service_issues')}")
            
        else:
            print(f"❌ API ERROR: Status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")
        import traceback
        traceback.print_exc()

def check_api_server():
    """Check if API server is running"""
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        return True
    except:
        return False

if __name__ == "__main__":
    print("🚀 STARTING WINBACK FRONTEND FORMAT TEST")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not check_api_server():
        print("❌ API SERVER NOT RUNNING!")
        print("   Please make sure FastAPI server is running on http://localhost:8000")
        sys.exit(1)
        
    print("✅ API SERVER IS RUNNING")
    print()
    
    test_winback_frontend_format()
    
    print("\n" + "="*80)
    print("✅ WINBACK FRONTEND FORMAT TEST COMPLETED")
    print("="*80)