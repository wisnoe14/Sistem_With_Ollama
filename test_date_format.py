#!/usr/bin/env python3
"""
Test script khusus untuk melihat format estimasi pembayaran dengan tanggal
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_date_format_in_prediction():
    """Test format tanggal di estimasi pembayaran"""
    
    print("🗓️ Testing Date Format in Estimasi Pembayaran")
    print("=" * 60)
    
    try:
        # Import prediction endpoint logic
        from app.api.v1.endpoints.conversation import predict_final_endpoint
        from app.schemas.conversation import FinalPredictRequest
        
        # Test data
        test_cases = [
            {
                "name": "Telecollection - SUDAH BAYAR",
                "data": {
                    "topic": "telecollection",
                    "customer_id": "ICON12345",
                    "conversation": [
                        {"q": "Status dihubungi?", "a": "Terhubung"},
                        {"q": "Apakah ada kendala dalam pembayaran?", "a": "Tidak ada, sudah siap bayar"}
                    ]
                }
            },
            {
                "name": "Telecollection - AKAN BAYAR",
                "data": {
                    "topic": "telecollection", 
                    "customer_id": "ICON12345",
                    "conversation": [
                        {"q": "Status dihubungi?", "a": "Terhubung"},
                        {"q": "Kapan Anda berencana melakukan pembayaran?", "a": "Besok saya bayar"}
                    ]
                }
            },
            {
                "name": "Winback - TERTARIK",
                "data": {
                    "topic": "winback",
                    "customer_id": "ICON67890",
                    "conversation": [
                        {"q": "Status dihubungi?", "a": "Terhubung"},
                        {"q": "Apakah Anda berminat mengaktifkan kembali layanan?", "a": "Iya saya mau coba lagi"}
                    ]
                }
            },
            {
                "name": "Retention - LOYAL",
                "data": {
                    "topic": "retention",
                    "customer_id": "ICON11111", 
                    "conversation": [
                        {"q": "Status dihubungi?", "a": "Terhubung"},
                        {"q": "Bagaimana kepuasan Anda dengan layanan kami?", "a": "Sangat puas dan loyal"}
                    ]
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test {i}: {test_case['name']}")
            
            # Create request object
            class MockRequest:
                def __init__(self, data):
                    self.topic = data["topic"]
                    self.customer_id = data["customer_id"] 
                    self.conversation = data["conversation"]
            
            mock_req = MockRequest(test_case["data"])
            
            # Call prediction endpoint
            result = predict_final_endpoint(mock_req)
            prediction = result.get("result", {})
            
            # Display results
            print(f"📊 Keputusan: {prediction.get('keputusan', 'N/A')}")
            print(f"📅 Estimasi Pembayaran: {prediction.get('estimasi_pembayaran', 'N/A')}")
            print(f"🎯 Status: {prediction.get('status', 'N/A')}")
            print(f"📝 Alasan: {prediction.get('alasan', 'N/A')[:50]}...")
            
            if test_case["data"]["topic"] in ["winback", "retention"]:
                print(f"💫 Minat Berlangganan: {prediction.get('minat_berlangganan', 'N/A')}")
                print(f"🎁 Jenis Promo: {prediction.get('jenis_promo', 'N/A')}")
            
            print("-" * 40)
            
    except ImportError as e:
        print(f"⚠️  Cannot import modules: {e}")
        print("   Make sure you're running from the right directory")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_date_components():
    """Test komponen tanggal yang digunakan"""
    
    print(f"\n🗓️ Current Date Components")
    print("=" * 30)
    
    from datetime import datetime, timedelta
    
    now = datetime.now()
    print(f"📅 Hari ini: {now.strftime('%d %B %Y')}")
    print(f"📅 Besok: {(now + timedelta(days=1)).strftime('%d %B %Y')}")
    print(f"📅 +2 hari: {(now + timedelta(days=2)).strftime('%d %B %Y')}")
    print(f"📅 +7 hari: {(now + timedelta(days=7)).strftime('%d %B %Y')}")
    print(f"📅 +10 hari: {(now + timedelta(days=10)).strftime('%d %B %Y')}")
    print(f"📅 +14 hari: {(now + timedelta(days=14)).strftime('%d %B %Y')}")
    print(f"📅 +30 hari: {(now + timedelta(days=30)).strftime('%d %B %Y')}")

if __name__ == "__main__":
    test_date_components()
    test_date_format_in_prediction()
    print(f"\n🎯 Date Format Test Complete!")