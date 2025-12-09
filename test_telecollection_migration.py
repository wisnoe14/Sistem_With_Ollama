"""
Test untuk memastikan migrasi telecollection_service berfungsi dengan baik
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_telecollection_migration():
    """Test apakah telecollection service bisa di-import dan digunakan"""
    
    print("\n" + "="*70)
    print("TEST: Telecollection Service Migration")
    print("="*70)
    
    # Test 1: Import from new service
    print("\n[TEST 1] Import dari telecollection_services...")
    try:
        from app.services.telecollection_services import predict_outcome as new_predict
        print("✅ Import berhasil dari telecollection_services")
    except ImportError as e:
        print(f"❌ Gagal import dari telecollection_services: {e}")
        return False
    
    # Test 2: Import from old gpt_service (should redirect)
    print("\n[TEST 2] Import dari gpt_service (backward compatibility)...")
    try:
        from app.services.gpt_service import predict_telecollection_outcome as old_predict
        print("✅ Import berhasil dari gpt_service (redirect)")
    except ImportError as e:
        print(f"❌ Gagal import dari gpt_service: {e}")
        return False
    
    # Test 3: Test basic functionality with new service
    print("\n[TEST 3] Test fungsi dengan conversation kosong...")
    try:
        result = new_predict([])
        print(f"✅ Fungsi berjalan, keputusan: {result.get('keputusan')}")
        assert 'keputusan' in result
        assert 'alasan' in result
        assert 'risk_level' in result
        print(f"   Risk level: {result.get('risk_level')}, {result.get('risk_label')}")
    except Exception as e:
        print(f"❌ Error saat test fungsi: {e}")
        return False
    
    # Test 4: Test with sample conversation
    print("\n[TEST 4] Test dengan sample conversation...")
    sample_conversation = [
        {
            "q": "Pak, tagihan Bapak sudah jatuh tempo. Kapan bisa bayar?",
            "a": "Oh iya, saya besok mau bayar kok.",
            "goal": "payment_timeline"
        }
    ]
    try:
        result = new_predict(sample_conversation)
        print(f"✅ Fungsi berjalan dengan conversation")
        print(f"   Keputusan: {result.get('keputusan')}")
        print(f"   Probability: {result.get('probability')}%")
        print(f"   Risk: {result.get('risk_label')} ({result.get('risk_color')})")
        print(f"   Alasan: {result.get('alasan')[:80]}...")
    except Exception as e:
        print(f"❌ Error saat test dengan conversation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Verify backward compatibility
    print("\n[TEST 5] Test backward compatibility (gpt_service redirect)...")
    try:
        result_old = old_predict(sample_conversation)
        result_new = new_predict(sample_conversation)
        
        # Both should produce same keputusan (might differ in details due to randomness)
        assert result_old.get('keputusan') == result_new.get('keputusan')
        print(f"✅ Backward compatibility OK")
        print(f"   Old: {result_old.get('keputusan')}")
        print(f"   New: {result_new.get('keputusan')}")
    except Exception as e:
        print(f"❌ Error backward compatibility: {e}")
        return False
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    return True


if __name__ == "__main__":
    print("\n🚀 Starting telecollection service migration test...")
    
    success = test_telecollection_migration()
    
    if success:
        print("\n✅ Migration successful! telecollection_service is ready to use.")
        print("\nRecommendations:")
        print("1. Update imports to use: from app.services.telecollection_service import predict_telecollection_outcome")
        print("2. Old imports from gpt_service will still work (with deprecation warning)")
        print("3. Consider migrating winback and retention services similarly")
    else:
        print("\n❌ Migration test failed!")
        sys.exit(1)
