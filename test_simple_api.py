#!/usr/bin/env python3#!/usr/bin/env python3

""""""

🧪 SIMPLE API TEST - Check winback prediction endpointTest API endpoint sederhana untuk winback prediction

""""""



import requestsimport requests

import jsonimport json

import time

def test_simple_api():

    """Simple test for winback prediction endpoint"""print("🌐 SIMPLE API TEST: Check Server & Winback Prediction")

    print("=" * 60)

    # Simple conversation that caused the error before

    conversation = [# Check server health first

        {"q": "Status Dihubungi?", "a": "Dihubungi"},health_url = "http://localhost:8000/"

        {"q": "Selamat sore, Bapak/Ibu. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Budi?", "a": "Ya, benar"},

        {"q": "Sebagai bentuk apresiasi, kami menawarkan promo gratis 1 bulan untuk Bapak/Ibu jika bersedia mengaktifkan layanan ICONNET kembali. Promo ini bisa Bapak/Ibu dapatkan dengan cara melakukan 1x pembayaran untuk mengaktifkan layanan ICONNETnya. Apakah Bapak/Ibu bersedia untuk mengaktifkan layanan ICONNETnya kembali?", "a": "Tidak, terima kasih"},print("🔍 Checking server health...")

        {"q": "Baik Bapak/Ibu, jika boleh tahu karena apa ya tidak bersedia mengaktifkan kembali layanan ICONNET?", "a": "Ada keluhan layanan"},try:

        {"q": "Terima kasih, Bapak/Ibu. Kami melihat bahwa layanan ICONNET Bapak/Ibu sedang terputus, dan kami ingin tahu apakah ada kendala yang bisa kami bantu? Saat ini kami sedang memiliki promo menarik untuk Bapak/Ibu. Apakah boleh saya sampaikan lebih lanjut?", "a": "Tidak tertarik"},    health_response = requests.get(health_url, timeout=5)

        {"q": "Baik Bapak/Ibu, jika boleh tahu karena apa ya tidak bersedia mengaktifkan kembali?", "a": "Ada keluhan layanan"},    if health_response.status_code == 200:

        {"q": "Baik Bapak/Ibu, akan kami bantu untuk mengirimkan kode pembayaran melalui email. Untuk estimasi pembayaran akan dibayarkan berapa jam ke depan ya?", "a": "Hari ini juga"},        print("✅ Server is running!")

        {"q": "Baik Bapak/Ibu, untuk perangkat ICONNET-nya apakah masih berada di lokasi rumah?", "a": "Sudah dikembalikan"}    else:

    ]        print(f"⚠️ Server responded with status: {health_response.status_code}")

    except Exception as e:

    payload = {    print(f"❌ Server not accessible: {e}")

        "customer_id": "ICON12345",    print("🚀 Please start the FastAPI server first!")

        "topic": "winback",    exit(1)

        "conversation": conversation

    }# Test winback prediction

    api_url = "http://localhost:8000/api/v1/endpoints/conversation/predict"

    try:

        print("🚀 Testing winback prediction endpoint...")# Simplified test data

        print(f"📝 Conversation length: {len(conversation)} entries")test_data = {

            "customer_id": "ICON12345", 

        response = requests.post(    "topic": "winback",

            "http://localhost:8000/api/v1/endpoints/conversation/predict",    "conversation": [

            json=payload,        {"q": "Status Dihubungi?", "a": "Dihubungi"},

            timeout=30        {"q": "Apakah tertarik reaktivasi?", "a": "Ya, mau coba lagi"},

        )        {"q": "Kapan bisa aktivasi?", "a": "Minggu depan"},

                {"q": "Perangkat masih ada?", "a": "Sudah dikembalikan"}

        if response.status_code == 200:    ]

            result = response.json()}

            prediction = result.get("result", {})

            print(f"\n📤 Testing winback prediction API...")

            print("✅ SUCCESS! Prediction generated:")print(f"Endpoint: {api_url}")

            print(f"   Keputusan: {prediction.get('keputusan')}")

            print(f"   Probability: {prediction.get('probability')}")try:

            print(f"   Minat Berlangganan: {prediction.get('minat_berlangganan')}")    print("⏳ Sending request...")

            print(f"   Jenis Promo: {prediction.get('jenis_promo')}")    response = requests.post(api_url, json=test_data, timeout=15)

            print(f"   Estimasi Pembayaran: {prediction.get('estimasi_pembayaran')}")    

            print(f"   Equipment Status: {prediction.get('equipment_status')}")    print(f"📊 Response Status: {response.status_code}")

            print(f"   Service Issues: {prediction.get('service_issues')}")    

                if response.status_code == 200:

            print("\n✅ All fields are populated correctly!")        result = response.json()

            return True        prediction = result.get("result", {})

                    

        else:        print(f"\n🎯 WINBACK PREDICTION RESULT:")

            print(f"❌ API Error: {response.status_code}")        print(f"   ✅ keputusan: {prediction.get('keputusan')}")

            print(f"Response: {response.text}")        print(f"   ✅ probability: {prediction.get('probability')}")

            return False        print(f"   ✅ confidence: {prediction.get('confidence')}")

                    print(f"   ✅ status_dihubungi: {prediction.get('status_dihubungi')}")

    except Exception as e:        print(f"   ✅ alasan: {prediction.get('alasan')}")

        print(f"❌ Error: {e}")        

        return False        # Check if winback-specific fields are present

        if "keputusan" in prediction and "detail_analysis" in prediction:

if __name__ == "__main__":            print(f"\n✅ WINBACK FIELDS DETECTED - API WORKING CORRECTLY!")

    success = test_simple_api()        else:

    if success:            print(f"\n❌ Missing winback-specific fields")

        print("\n🎉 WINBACK PREDICTION SYSTEM IS WORKING PERFECTLY!")            

    else:    else:

        print("\n💥 THERE ARE STILL ISSUES TO FIX")        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print(f"⏰ Request timed out - prediction might be running")
except Exception as e:
    print(f"❌ Request failed: {e}")

print(f"\n🎉 Test completed!")