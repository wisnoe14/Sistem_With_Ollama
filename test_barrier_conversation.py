#!/usr/bin/env python3
"""
Test conversation flow untuk customer yang memberikan informasi barrier spesifik
Memastikan tidak ada pertanyaan berulang dan prediction yang tepat
"""
import requests
import json

def test_honest_financial_barrier():
    """Test customer yang jujur tentang kesulitan finansial"""
    base_url = "http://127.0.0.1:8000"
    
    # Simulasi conversation dengan barrier jujur
    conversation_data = {
        "customer_id": "ICON12345",
        "conversation_type": "telecollection",
        "questions": [
            "Baik Bapak/Ibu, saya dari ICON+. Terkait tagihan internet bulan ini yang sudah jatuh tempo, apakah Bapak/Ibu bisa melakukan pembayaran hari ini?",
            "Saya memahami situasinya Pak/Bu. Kalau begitu, kapan Bapak/Ibu perkirakan bisa melakukan pembayaran? Apakah dalam 2-3 hari ke depan memungkinkan?",
            "Baik Pak/Bu, terkait hambatan pembayaran yang Bapak/Ibu sebutkan, apakah ada alternatif solusi yang bisa kita diskusikan?",
        ],
        "answers": [
            "belum ada uang pak, gaji belum masuk",
            "besok gajian sih, tapi harus bayar ini itu dulu",
            "selesai pak, nanti saya hubungi lagi kalau sudah ada uang"
        ]
    }
    
    print("🧪 Testing conversation dengan honest financial barrier...")
    print("Customer responses:", conversation_data["answers"])
    
    try:
        # Send conversation untuk processing
        response = requests.post(
            f"{base_url}/api/v1/conversation/process",
            json=conversation_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Status: {result.get('status')}")
            print(f"📊 Prediction: {result.get('prediction')}")
            print(f"🎯 Confidence: {result.get('confidence')}")
            print(f"💭 Alasan: {result.get('alasan')}")
            
            # Validasi hasil
            prediction = result.get('prediction')
            confidence = result.get('confidence', 0)
            alasan = result.get('alasan', '')
            
            # Ekspektasi: Harusnya UNCERTAIN atau FOLLOW_UP, bukan REJECT
            if prediction in ['UNCERTAIN', 'FOLLOW_UP']:
                print("\n✅ PASS: Prediction yang tepat untuk honest financial barrier")
            else:
                print(f"\n❌ FAIL: Prediction '{prediction}' terlalu keras untuk honest barrier")
            
            # Cek apakah ada kata-kata yang menunjukkan pemahaman
            if any(word in alasan.lower() for word in ['tantangan finansial', 'jujur', 'fleksibel']):
                print("✅ PASS: Alasan menunjukkan pemahaman terhadap situasi customer")
            else:
                print("❌ FAIL: Alasan terlalu keras untuk situasi finansial yang jujur")
                
            # Cek confidence score
            if prediction == 'UNCERTAIN' and 0.4 <= confidence <= 0.7:
                print("✅ PASS: Confidence score appropriate untuk uncertain case")
            else:
                print(f"⚠️  INFO: Confidence {confidence} untuk prediction {prediction}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

def test_strong_negative_response():
    """Test customer dengan strong negative response"""
    base_url = "http://127.0.0.1:8000"
    
    conversation_data = {
        "customer_id": "ICON67890", 
        "conversation_type": "telecollection",
        "questions": [
            "Selamat siang Bapak/Ibu, saya dari ICON+. Terkait tagihan internet yang sudah jatuh tempo, apakah bisa melakukan pembayaran hari ini?",
            "Baik Pak/Bu, apakah ada kendala khusus yang membuat Bapak/Ibu tidak bisa melakukan pembayaran?",
        ],
        "answers": [
            "tidak mampu pak, mau putus saja internetnya",
            "mahal, tidak cocok lagi, cancel saja"
        ]
    }
    
    print("\n🧪 Testing conversation dengan strong negative response...")
    print("Customer responses:", conversation_data["answers"])
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/conversation/process",
            json=conversation_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Status: {result.get('status')}")
            print(f"📊 Prediction: {result.get('prediction')}")
            print(f"🎯 Confidence: {result.get('confidence')}")
            print(f"💭 Alasan: {result.get('alasan')}")
            
            # Validasi: Harusnya REJECT untuk strong negative
            prediction = result.get('prediction')
            if prediction == 'REJECT':
                print("✅ PASS: Prediction REJECT tepat untuk strong negative response")
            else:
                print(f"⚠️  INFO: Prediction '{prediction}' untuk strong negative")
                
        else:
            print(f"❌ Error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Enhanced Conversation Flow & Prediction Logic")
    print("="*60)
    
    # Test kedua scenario
    test_honest_financial_barrier()
    test_strong_negative_response()
    
    print("\n" + "="*60)
    print("✨ Testing completed!")