#!/usr/bin/env python3
"""
Test script untuk memastikan prediction endpoint menghasilkan format yang kompatibel dengan frontend
"""

import requests
import json

# Test data - simulasi conversation telecollection yang realistis
test_conversations = [
    {
        "topic": "telecollection",
        "customer_id": "ICON12345",
        "conversation": [
            {"q": "Status dihubungi?", "a": "Terhubung"},
            {"q": "Apakah Anda sudah mengetahui tagihan bulan ini?", "a": "Ya, saya tahu ada tagihan"},
            {"q": "Berapa tagihan yang harus Anda bayar?", "a": "Sekitar 300 ribuan"},
            {"q": "Kapan Anda berencana melakukan pembayaran?", "a": "Besok saya bayar"},
            {"q": "Apakah ada kendala dalam pembayaran?", "a": "Tidak ada, sudah siap bayar"},
            {"q": "Metode pembayaran apa yang akan Anda gunakan?", "a": "Transfer bank"}
        ]
    },
    {
        "topic": "winback",
        "customer_id": "ICON67890", 
        "conversation": [
            {"q": "Status dihubungi?", "a": "Terhubung"},
            {"q": "Mengapa Anda berhenti berlangganan?", "a": "Paket terlalu mahal"},
            {"q": "Kami ada promo khusus dengan diskon 50%. Apakah Anda tertarik?", "a": "Wah menarik juga ya"},
            {"q": "Berapa budget yang Anda siapkan untuk internet?", "a": "Maksimal 200 ribu"},
            {"q": "Apakah Anda berminat mengaktifkan kembali layanan?", "a": "Iya saya mau coba lagi"}
        ]
    },
    {
        "topic": "retention",
        "customer_id": "ICON11111",
        "conversation": [
            {"q": "Status dihubungi?", "a": "Terhubung"},
            {"q": "Bagaimana kepuasan Anda dengan layanan kami?", "a": "Puas sih tapi mahal"},
            {"q": "Apakah Anda berencana berpindah provider?", "a": "Lagi mikir-mikir"},
            {"q": "Kami bisa berikan upgrade gratis selama 3 bulan. Tertarik?", "a": "Boleh juga tuh"},
            {"q": "Apakah ada keluhan dengan layanan saat ini?", "a": "Kadang lemot pas hujan"}
        ]
    }
]

def test_prediction_endpoint(base_url="http://localhost:8000"):
    """Test prediction endpoint dengan berbagai skenario"""
    
    print("🧪 Testing Prediction Endpoint for Frontend Compatibility")
    print("=" * 60)
    
    for i, test_data in enumerate(test_conversations, 1):
        topic = test_data["topic"]
        customer_id = test_data["customer_id"]
        
        print(f"\n📋 Test {i}: {topic.upper()} - {customer_id}")
        print(f"Conversation steps: {len(test_data['conversation'])}")
        
        try:
            # Call prediction endpoint
            response = requests.post(
                f"{base_url}/api/v1/conversations/predict",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                prediction = result.get("result", {})
                
                print(f"✅ Status: {response.status_code}")
                print(f"📊 Prediction Result:")
                
                # Check frontend-required fields
                required_fields = [
                    "status", "alasan", "confidence", "probability", 
                    "estimasi_pembayaran", "jenis_promo", "minat_berlangganan"
                ]
                
                for field in required_fields:
                    value = prediction.get(field, "NOT_SET")
                    print(f"   • {field}: {value}")
                
                # Check enhanced fields
                enhanced_fields = ["keputusan", "probability_score", "confidence_level"]
                if any(prediction.get(field) for field in enhanced_fields):
                    print(f"🔬 Enhanced Fields:")
                    for field in enhanced_fields:
                        if field in prediction:
                            print(f"   • {field}: {prediction[field]}")
                            
                # Topic-specific validation
                if topic == "telecollection":
                    estimasi = prediction.get("estimasi_pembayaran", "")
                    if estimasi and estimasi != "Tidak dapat ditentukan":
                        print(f"✅ Telecollection: Valid payment estimate")
                    else:
                        print(f"⚠️  Telecollection: Generic payment estimate")
                        
                elif topic == "winback":
                    minat = prediction.get("minat_berlangganan", "")
                    promo = prediction.get("jenis_promo", "")
                    if minat and promo:
                        print(f"✅ Winback: Interest & promo set properly")
                    else:
                        print(f"⚠️  Winback: Missing interest/promo info")
                        
                elif topic == "retention":
                    minat = prediction.get("minat_berlangganan", "")
                    promo = prediction.get("jenis_promo", "")
                    if minat and promo:
                        print(f"✅ Retention: Loyalty fields set properly")
                    else:
                        print(f"⚠️  Retention: Missing loyalty info")
                
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed - Is server running on {base_url}?")
        except Exception as e:
            print(f"❌ Error: {e}")
            
        print("-" * 40)

def test_local_prediction():
    """Test prediction secara lokal tanpa server"""
    
    print("\n🔬 Testing Local Prediction Functions")
    print("=" * 60)
    
    try:
        # Import local functions
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from app.services.gpt_service import generate_final_prediction
        
        for i, test_data in enumerate(test_conversations, 1):
            topic = test_data["topic"]
            conversation = test_data["conversation"]
            
            print(f"\n📋 Local Test {i}: {topic.upper()}")
            
            result = generate_final_prediction(topic, conversation)
            
            print(f"📊 Direct Prediction Result:")
            for key, value in result.items():
                print(f"   • {key}: {value}")
                
    except ImportError as e:
        print(f"⚠️  Cannot test locally: {e}")
        print("   Run server test instead")

if __name__ == "__main__":
    # Test endpoint if server is running
    test_prediction_endpoint()
    
    # Test local functions
    test_local_prediction()
    
    print(f"\n🎯 Frontend Compatibility Check Complete!")
    print(f"   Make sure all required fields are present for proper display")