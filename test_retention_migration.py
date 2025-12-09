"""
Test script for retention service migration verification.

This script verifies that:
1. The retention service can be imported correctly
2. The prediction function works as expected
3. Backward compatibility is maintained in gpt_service
4. All key features are preserved in the migration
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def test_retention_import():
    """Test 1: Verify retention service can be imported."""
    print("\n" + "="*60)
    print("TEST 1: Import retention_services")
    print("="*60)
    
    try:
        from app.services import retention_services
        print("✅ Successfully imported retention_services")
        
        # Check for key functions
        assert hasattr(retention_services, 'predict_outcome'), "Missing predict_outcome"
        assert hasattr(retention_services, 'generate_question'), "Missing generate_question"
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
        from app.services import retention_services
        
        # Test with loyal customer conversation
        test_conversation = [
            {"q": "Bagaimana pengalaman Anda dengan layanan kami?", "a": "Puas, layanan bagus"},
            {"q": "Berapa lama sudah berlangganan?", "a": "Sudah 2 tahun, setia dengan ICONNET"},
            {"q": "Ada keluhan?", "a": "Tidak ada, saya cocok dengan layanan ini"}
        ]
        
        result = retention_services.predict_outcome(test_conversation)
        
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
        assert "satisfaction_score" in result["detail_analysis"], "Missing satisfaction_score"
        assert "churn_risk_score" in result["detail_analysis"], "Missing churn_risk_score"
        assert "loyalty_score" in result["detail_analysis"], "Missing loyalty_score"
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
            {"q": "Bagaimana layanan kami?", "a": "Mau pindah ke provider lain"}
        ]
        
        # Call old function name
        result = gpt_service.predict_retention_outcome(test_conversation)
        
        assert "keputusan" in result, "Old function doesn't return valid result"
        print(f"✅ Old function call works: {result['keputusan']}")
        print(f"✅ Backward compatibility maintained")
        return True
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_satisfaction_detection():
    """Test 4: Verify satisfaction indicator detection."""
    print("\n" + "="*60)
    print("TEST 4: Satisfaction Detection")
    print("="*60)
    
    try:
        from app.services import retention_services
        
        # Conversation with satisfaction
        test_conversation = [
            {"q": "Bagaimana pengalaman Anda?", "a": "Sangat puas dengan layanan ICONNET"},
            {"q": "Apakah Anda senang?", "a": "Iya, sangat senang dan nyaman"}
        ]
        
        result = retention_services.predict_outcome(test_conversation)
        
        assert result["detail_analysis"]["satisfaction_score"] > 50, "Satisfaction not detected"
        print(f"✅ Satisfaction score: {result['detail_analysis']['satisfaction_score']:.1f}")
        print(f"✅ Satisfaction indicators detected correctly")
        
        return True
    except Exception as e:
        print(f"❌ Satisfaction detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_churn_risk_detection():
    """Test 5: Verify churn risk detection."""
    print("\n" + "="*60)
    print("TEST 5: Churn Risk Detection")
    print("="*60)
    
    try:
        from app.services import retention_services
        
        # Conversation with churn risk
        test_conversation = [
            {"q": "Ada masalah?", "a": "Iya, sering gangguan, lambat terus"},
            {"q": "Apakah mau pindah?", "a": "Mau ganti ke Indihome saja"}
        ]
        
        result = retention_services.predict_outcome(test_conversation)
        
        assert result["detail_analysis"]["churn_risk_score"] > 0, "Churn risk not detected"
        assert result["detail_analysis"]["competitive_mentions"] > 0, "Competitor mention not detected"
        assert result["detail_analysis"]["service_complaints"] > 0, "Service complaints not detected"
        
        print(f"✅ Churn risk score: {result['detail_analysis']['churn_risk_score']:.1f}")
        print(f"✅ Service complaints: {result['detail_analysis']['service_complaints']}")
        print(f"✅ Competitor mentions: {result['detail_analysis']['competitive_mentions']}")
        print(f"✅ Decision: {result['keputusan']}")
        print(f"✅ Churn risk detected correctly")
        
        return True
    except Exception as e:
        print(f"❌ Churn risk detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_loyalty_detection():
    """Test 6: Verify loyalty indicator detection."""
    print("\n" + "="*60)
    print("TEST 6: Loyalty Detection")
    print("="*60)
    
    try:
        from app.services import retention_services
        
        # Conversation with loyalty
        test_conversation = [
            {"q": "Berapa lama berlangganan?", "a": "Sudah lama, dari tahun 2020"},
            {"q": "Mau lanjut?", "a": "Iya, setia dengan ICONNET, mau bertahan"}
        ]
        
        result = retention_services.predict_outcome(test_conversation)
        
        assert result["detail_analysis"]["loyalty_score"] > 0, "Loyalty not detected"
        print(f"✅ Loyalty score: {result['detail_analysis']['loyalty_score']:.1f}")
        print(f"✅ Loyalty indicators detected correctly")
        
        return True
    except Exception as e:
        print(f"❌ Loyalty detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests and report results."""
    print("\n" + "="*60)
    print("RETENTION SERVICE MIGRATION TEST SUITE")
    print("="*60)
    
    tests = [
        ("Import Test", test_retention_import),
        ("Prediction Functionality", test_prediction_functionality),
        ("Backward Compatibility", test_backward_compatibility),
        ("Satisfaction Detection", test_satisfaction_detection),
        ("Churn Risk Detection", test_churn_risk_detection),
        ("Loyalty Detection", test_loyalty_detection),
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
