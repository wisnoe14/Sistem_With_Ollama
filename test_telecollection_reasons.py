#!/usr/bin/env python3
"""
Test enhanced telecollection prediction reasons
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from datetime import datetime

def test_telecollection_reasons():
    """Test telecollection prediction with enhanced reasons"""
    
    print("="*80)
    print("🎯 TESTING TELECOLLECTION PREDICTION - ENHANCED REASONS")
    print("="*80)
    
    # Test Case 1: Strong commitment with specific date
    test_case_1 = {
        "name": "Strong Commitment with Date",
        "conversation": [
            {"q": "Status Dihubungi?", "a": "Bisa Dihubungi"},
            {"q": "Halo, selamat pagi! Saya dari ICONNET mau mengingatkan tagihan bulan ini ya. Sudah sempat dibayar belum?", "a": "Belum, tapi akan bayar"},
            {"q": "Baik, kira-kira kapan bisa dibayar ya?", "a": "Besok sore akan saya transfer"},
            {"q": "Oke, transfernya lewat mana ya?", "a": "Lewat mobile banking BCA"},
            {"q": "Baik, besok sore ya. Terima kasih!", "a": "Siap, pasti akan saya bayar besok"}
        ]
    }
    
    # Test Case 2: Payment barriers with cooperation
    test_case_2 = {
        "name": "Payment Barriers with Cooperation", 
        "conversation": [
            {"q": "Status Dihubungi?", "a": "Bisa Dihubungi"},
            {"q": "Halo, untuk tagihan ICONNET bulan ini sudah bisa dibayar?", "a": "Maaf, lagi ada kendala keuangan"},
            {"q": "Oh begitu, kendalanya seperti apa ya?", "a": "Gaji belum turun, biasanya tanggal 15"},
            {"q": "Baik, jadi setelah tanggal 15 bisa dibayar ya?", "a": "Iya, insyaallah bisa"},
            {"q": "Oke, kami follow up setelah tanggal 15 ya", "a": "Baik, terima kasih pengertiannya"}
        ]
    }
    
    # Test Case 3: Already paid
    test_case_3 = {
        "name": "Already Paid",
        "conversation": [
            {"q": "Status Dihubungi?", "a": "Bisa Dihubungi"},
            {"q": "Selamat pagi, untuk tagihan ICONNET bulan ini sudah dibayar ya?", "a": "Sudah bayar kemarin"},
            {"q": "Baik, lewat mana pembayarannya?", "a": "Lewat ATM BRI kemarin malam"},
            {"q": "Oke terima kasih informasinya", "a": "Sama-sama"}
        ]
    }
    
    # Test Case 4: Multiple barriers - difficult payment
    test_case_4 = {
        "name": "Multiple Barriers - Difficult Payment",
        "conversation": [
            {"q": "Status Dihubungi?", "a": "Bisa Dihubungi"},
            {"q": "Untuk tagihan bulan ini bisa dibayar kapan ya?", "a": "Susah sekarang, lagi krisis"},
            {"q": "Kendalanya apa ya?", "a": "Usaha tutup karena pandemi"},
            {"q": "Bisa cicil atau gimana?", "a": "Gak ada uang sama sekali"},
            {"q": "Oke, bagaimana solusinya ya?", "a": "Entahlah, susah banget sekarang"}
        ]
    }
    
    test_cases = [test_case_1, test_case_2, test_case_3, test_case_4]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 TEST CASE {i}: {test_case['name']}")
        print("="*60)
        
        payload = {
            "customer_id": f"TEST{i:03d}",
            "topic": "telecollection",
            "conversation": test_case['conversation']
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/endpoints/conversation/predict",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                prediction = result.get("result", {})
                
                print(f"✅ PREDICTION RESULT:")
                print(f"   Keputusan: {prediction.get('keputusan')}")
                print(f"   Probability: {prediction.get('probability')}")
                print(f"   Confidence: {prediction.get('confidence')}")
                print(f"\n📝 ENHANCED REASON:")
                print(f"   {prediction.get('alasan', 'No reason provided')}")
                
                # Show additional telecollection fields
                print(f"\n🎯 TELECOLLECTION FIELDS:")
                print(f"   Estimasi Pembayaran: {prediction.get('estimasi_pembayaran', 'N/A')}")
                print(f"   Payment Method: {prediction.get('payment_method', 'N/A')}")
                print(f"   Urgency Level: {prediction.get('urgency_level', 'N/A')}")
                print(f"   Financial Capability: {prediction.get('financial_capability', 'N/A')}")
                
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

def check_api_server():
    """Check if API server is running"""
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        return True
    except:
        return False

if __name__ == "__main__":
    print("🚀 STARTING TELECOLLECTION ENHANCED REASONS TEST")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not check_api_server():
        print("❌ API SERVER NOT RUNNING!")
        print("   Please make sure FastAPI server is running on http://localhost:8000")
        sys.exit(1)
        
    print("✅ API SERVER IS RUNNING")
    
    test_telecollection_reasons()
    
    print("\n" + "="*80)
    print("✅ TELECOLLECTION ENHANCED REASONS TEST COMPLETED")
    print("="*80)