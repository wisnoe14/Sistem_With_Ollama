"""
Test script for winback service migration verification.

This script verifies that:
1. The winback service can be imported correctly
2. The prediction function works as expected
3. Backward compatibility is maintained in gpt_service
4. All key features are preserved in the migration
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def test_winback_import():
    """Test 1: Verify winback service can be imported."""
    print("\n" + "="*60)
    print("TEST 1: Import winback_services")
    print("="*60)
    
    try:
        from app.services import winback_services
        print("✅ Successfully imported winback_services")
        
        # Check for key functions
        assert hasattr(winback_services, 'predict_outcome'), "Missing predict_outcome"
        assert hasattr(winback_services, 'generate_question'), "Missing generate_question"
        print("✅ All required functions present")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_prediction_functionality():
    """Test 2: Verify prediction works correctly."""
    print("\n" + "="*60)
    print("TEST 2: Prediction Functionality")
    print("="*60)
    
    try:
        from app.services import winback_services
        
        # Test with sample conversation showing interest
        test_conversation = [
            {"q": "Mengapa Anda berhenti menggunakan layanan kami?", "a": "Karena sering gangguan"},
            {"q": "Bagaimana kondisi perangkat?", "a": "Masih ada, kondisi normal"},
            {"q": "Kami ada promo comeback: Bayar 1 bulan gratis 1 bulan. Tertarik?", "a": "Wah boleh, menarik juga"}
        ]
        
        result = winback_services.predict_outcome(test_conversation)
        
        # Verify result structure
        required_keys = ["status_dihubungi", "keputusan", "probability", "confidence", 
                        "tanggal_prediksi", "alasan", "detail_analysis"]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
        
        print(f"✅ Prediction returned valid structure")
        print(f"   Keputusan: {result['keputusan']}")
        print(f"   Probability: {result['probability']}%")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Status: {result['status_dihubungi']}")
        
        # Verify detail_analysis
        assert "interest_score" in result["detail_analysis"], "Missing interest_score"
        assert "commitment_score" in result["detail_analysis"], "Missing commitment_score"
        print(f"✅ Detail analysis present")
        
        # Verify risk level fields
        assert "risk_level" in result, "Missing risk_level"
        assert "risk_label" in result, "Missing risk_label"
        assert "risk_color" in result, "Missing risk_color"
        print(f"✅ Risk indicators present: {result['risk_level']}")
        
        return True
    except Exception as e:
        print(f"❌ Prediction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """Test 3: Verify backward compatibility through gpt_service."""
    print("\n" + "="*60)
    print("TEST 3: Backward Compatibility")
    print("="*60)
    
    try:
        from app.services import gpt_service
        
        test_conversation = [
            {"q": "Kenapa berhenti?", "a": "Sudah pakai provider lain"}
        ]
        
        # Call old function name
        result = gpt_service.predict_winback_outcome(test_conversation)
        
        assert "keputusan" in result, "Old function doesn't return valid result"
        print(f"✅ Old function call works: {result['keputusan']}")
        print(f"✅ Backward compatibility maintained")
        return True
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_promo_detection():
    """Test 4: Verify promo discussion detection."""
    print("\n" + "="*60)
    print("TEST 4: Promo Detection")
    print("="*60)
    
    try:
        from app.services import winback_services
        
        # Conversation with promo in ANSWER (not just question)
        test_conversation = [
            {"q": "Kondisi perangkat?", "a": "Masih ada"},
            {"q": "Tertarik dengan layanan kami lagi?", "a": "Kalau ada promo mau"}
        ]
        
        result = winback_services.predict_outcome(test_conversation)
        
        assert result["detail_analysis"]["promo_discussed"] == True, "Promo not detected"
        print(f"✅ Promo discussion detected correctly")
        
        # Verify answer interpretations
        assert "jawaban_terinterpretasi" in result, "Missing jawaban_terinterpretasi"
        interpretations = result["jawaban_terinterpretasi"]
        
        # Check for promo-related entries
        promo_entries = [e for e in interpretations if e.get('promo_related')]
        print(f"✅ Found {len(promo_entries)} promo-related entries")
        
        return True
    except Exception as e:
        print(f"❌ Promo detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_objection_handling():
    """Test 5: Verify strong objection detection."""
    print("\n" + "="*60)
    print("TEST 5: Objection Handling")
    print("="*60)
    
    try:
        from app.services import winback_services
        
        # Conversation with strong rejection
        test_conversation = [
            {"q": "Kenapa berhenti?", "a": "Pindah rumah ke luar kota"},
            {"q": "Bisa reaktivasi di lokasi baru?", "a": "Tidak tertarik, sudah pakai provider lain"}
        ]
        
        result = winback_services.predict_outcome(test_conversation)
        
        assert result["detail_analysis"]["objection_count"] > 0, "Objections not counted"
        assert "TIDAK" in result["keputusan"].upper() or "FOLLOW" in result["keputusan"].upper(), \
               f"Wrong decision for strong rejection: {result['keputusan']}"
        
        print(f"✅ Objection count: {result['detail_analysis']['objection_count']}")
        print(f"✅ Decision: {result['keputusan']}")
        print(f"✅ Strong rejections handled correctly")
        
        return True
    except Exception as e:
        print(f"❌ Objection handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests and report results."""
    print("\n" + "="*60)
    print("WINBACK SERVICE MIGRATION TEST SUITE")
    print("="*60)
    
    tests = [
        ("Import Test", test_winback_import),
        ("Prediction Functionality", test_prediction_functionality),
        ("Backward Compatibility", test_backward_compatibility),
        ("Promo Detection", test_promo_detection),
        ("Objection Handling", test_objection_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Migration successful!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
