#!/usr/bin/env python3
"""
Test final verification of conversation flow improvements
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import predict_telecollection_status

def test_prediction_improvements():
    """Test that prediction improvements work correctly"""
    print("=" * 60)
    print("🚀 FINAL VERIFICATION: Conversation Flow & Prediction Fixes")
    print("=" * 60)
    
    test_cases = [
        {
            "conversation": "Apakah saya berbicara dengan Bapak yang pernah menggunakan layanan ICONNET? Ya benar. Baik, jadi ada tagihan yang belum diselesaikan sebesar Rp 450.000. Kapan bisa diselesaikan? belum ada uang",
            "answers": ["ya benar", "belum ada uang"], 
            "expected": "UNCERTAIN",
            "description": "Financial challenge 'belum ada uang' - should be UNCERTAIN not REJECT"
        },
        {
            "conversation": "Apakah saya berbicara dengan Bapak yang pernah menggunakan layanan ICONNET? Ya benar. Baik, jadi ada tagihan yang belum diselesaikan sebesar Rp 450.000. Kapan bisa diselesaikan? tidak mampu bayar mahal sekali",
            "answers": ["ya benar", "tidak mampu bayar mahal sekali"],
            "expected": "REJECT", 
            "description": "Strong rejection 'tidak mampu bayar mahal' - should be REJECT"
        },
        {
            "conversation": "Apakah saya berbicara dengan Bapak yang pernah menggunakan layanan ICONNET? Ya benar. Baik, jadi ada tagihan yang belum diselesaikan sebesar Rp 450.000. Kapan bisa diselesaikan? belum gajian tunggu tanggal 25",
            "answers": ["ya benar", "belum gajian tunggu tanggal 25"],
            "expected": "ACCEPT",
            "description": "Specific timeline 'tunggu tanggal 25' - should be ACCEPT (strong commitment)"
        },
        {
            "conversation": "Apakah saya berbicara dengan Bapak yang pernah menggunakan layanan ICONNET? Selesai",
            "answers": ["selesai"],
            "expected": "UNCERTAIN",
            "description": "Explicit closing 'selesai' - should be UNCERTAIN for short conversation"
        }
    ]
    
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 TEST {i}: {case['description']}")
        print(f"💬 Input: ...{case['answers'][-1]}")
        print(f"🎯 Expected: {case['expected']}")
        
        try:
            result = predict_telecollection_status(case['conversation'], case['answers'])
            
            actual_prediction = result.get('prediction', 'ERROR')
            confidence = result.get('confidence', 0.0)
            reason = result.get('reason', 'No reason')
            
            print(f"✅ Actual: {actual_prediction} (confidence: {confidence:.3f})")
            print(f"💭 Reason: {reason[:100]}...")
            
            success = actual_prediction == case['expected']
            print(f"{'✅ PASS' if success else '❌ FAIL'}")
            
            results.append({
                'test': i,
                'description': case['description'],
                'expected': case['expected'],
                'actual': actual_prediction,
                'success': success,
                'confidence': confidence
            })
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                'test': i,
                'description': case['description'],
                'expected': case['expected'],
                'actual': 'ERROR',
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"Test {result['test']}: {status} - {result['expected']} vs {result['actual']}")
    
    print(f"\n📈 Results: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Conversation flow improvements working correctly.")
    else:
        print("⚠️  Some tests failed. Review needed.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    test_prediction_improvements()