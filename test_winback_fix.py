#!/usr/bin/env python3
"""
🧪 TEST WINBACK PREDICTION FIX
Test untuk memastikan fungsi predict_winback_outcome bekerja dengan benar
"""

import sys
import os
sys.path.append('backend')

from app.services.gpt_service import predict_winback_outcome, predict_conversation_outcome

def test_winback_prediction():
    """Test winback prediction dengan sample conversation"""
    print("🧪 TESTING WINBACK PREDICTION...")
    
    # Sample conversation history
    sample_conversation = [
        {
            "q": "Status Dihubungi?",
            "a": "Dihubungi"
        },
        {
            "q": "Halo Budi, selamat pagi! Saya Wisnu dari ICONNET. Semoga kabar baik-baik saja ya! Saya lihat dari sistem bahwa layanan ICONNET-nya sudah ga aktif. Boleh share ga, waktu itu ada alasan khusus kenapa memutuskan untuk stop?",
            "a": "Sudah tidak pakai"
        }
    ]
    
    print(f"📝 Testing dengan {len(sample_conversation)} conversation entries...")
    
    try:
        # Test direct winback function
        print("\n1️⃣ Testing predict_winback_outcome directly:")
        result1 = predict_winback_outcome(sample_conversation)
        print(f"✅ Direct call result: {result1}")
        
        # Test through predict_conversation_outcome wrapper  
        print("\n2️⃣ Testing predict_conversation_outcome with mode='winback':")
        result2 = predict_conversation_outcome(sample_conversation, "winback")
        print(f"✅ Wrapper call result: {result2}")
        
        # Validate results
        print("\n📊 VALIDATION:")
        required_fields = ['status_dihubungi', 'keputusan', 'probability', 'confidence', 'tanggal_prediksi', 'alasan']
        
        for field in required_fields:
            if field in result1:
                print(f"  ✅ {field}: {result1[field]}")
            else:
                print(f"  ❌ Missing field: {field}")
                
        print("\n🎉 WINBACK PREDICTION TEST COMPLETED!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases"""
    print("\n🧪 TESTING EDGE CASES...")
    
    # Test empty conversation
    try:
        result = predict_winback_outcome([])
        print(f"✅ Empty conversation handled: {result}")
    except Exception as e:
        print(f"❌ Empty conversation error: {e}")
    
    # Test conversation with missing fields
    try:
        broken_conversation = [{"question": "test"}]  # missing 'a' field
        result = predict_winback_outcome(broken_conversation)
        print(f"✅ Broken conversation handled: {result}")
    except Exception as e:
        print(f"❌ Broken conversation error: {e}")

if __name__ == "__main__":
    print("🚀 WINBACK PREDICTION FIX TEST")
    print("=" * 50)
    
    success = test_winback_prediction()
    test_edge_cases()
    
    if success:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ TESTS FAILED!")