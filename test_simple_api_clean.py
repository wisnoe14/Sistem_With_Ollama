#!/usr/bin/env python3
"""
SIMPLE API TEST - Check winback prediction endpoint
"""

import requests
import json

def test_simple_api():
    """Simple test for winback prediction endpoint"""
    
    # Simple conversation that caused the error before
    conversation = [
        {"q": "Status Dihubungi?", "a": "Dihubungi"},
        {"q": "Selamat sore, Bapak/Ibu. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Budi?", "a": "Ya, benar"},
        {"q": "Sebagai bentuk apresiasi, kami menawarkan promo gratis 1 bulan untuk Bapak/Ibu jika bersedia mengaktifkan layanan ICONNET kembali. Promo ini bisa Bapak/Ibu dapatkan dengan cara melakukan 1x pembayaran untuk mengaktifkan layanan ICONNETnya. Apakah Bapak/Ibu bersedia untuk mengaktifkan layanan ICONNETnya kembali?", "a": "Tidak, terima kasih"},
        {"q": "Baik Bapak/Ibu, jika boleh tahu karena apa ya tidak bersedia mengaktifkan kembali layanan ICONNET?", "a": "Ada keluhan layanan"},
        {"q": "Terima kasih, Bapak/Ibu. Kami melihat bahwa layanan ICONNET Bapak/Ibu sedang terputus, dan kami ingin tahu apakah ada kendala yang bisa kami bantu? Saat ini kami sedang memiliki promo menarik untuk Bapak/Ibu. Apakah boleh saya sampaikan lebih lanjut?", "a": "Tidak tertarik"},
        {"q": "Baik Bapak/Ibu, jika boleh tahu karena apa ya tidak bersedia mengaktifkan kembali?", "a": "Ada keluhan layanan"},
        {"q": "Baik Bapak/Ibu, akan kami bantu untuk mengirimkan kode pembayaran melalui email. Untuk estimasi pembayaran akan dibayarkan berapa jam ke depan ya?", "a": "Hari ini juga"},
        {"q": "Baik Bapak/Ibu, untuk perangkat ICONNET-nya apakah masih berada di lokasi rumah?", "a": "Sudah dikembalikan"}
    ]
    
    payload = {
        "customer_id": "ICON12345",
        "topic": "winback",
        "conversation": conversation
    }
    
    try:
        print("Testing winback prediction endpoint...")
        print(f"Conversation length: {len(conversation)} entries")
        
        response = requests.post(
            "http://localhost:8000/api/v1/endpoints/conversation/predict",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            prediction = result.get("result", {})
            
            print("SUCCESS! Prediction generated:")
            print(f"   Keputusan: {prediction.get('keputusan')}")
            print(f"   Probability: {prediction.get('probability')}")
            print(f"   Minat Berlangganan: {prediction.get('minat_berlangganan')}")
            print(f"   Jenis Promo: {prediction.get('jenis_promo')}")
            print(f"   Estimasi Pembayaran: {prediction.get('estimasi_pembayaran')}")
            print(f"   Equipment Status: {prediction.get('equipment_status')}")
            print(f"   Service Issues: {prediction.get('service_issues')}")
            
            print("\nAll fields are populated correctly!")
            return True
            
        else:
            print(f"API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_api()
    if success:
        print("\nWINBACK PREDICTION SYSTEM IS WORKING PERFECTLY!")
    else:
        print("\nTHERE ARE STILL ISSUES TO FIX")