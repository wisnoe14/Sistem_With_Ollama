"""
Test comprehensive winback prediction scenarios
"""
from backend.app.services.gpt_service import predict_winback_outcome

test_cases = [
    {
        "name": "Pindah Rumah (Strong Rejection)",
        "conversation": [
            {'q': 'Greeting?', 'a': 'Ya, benar'},
            {'q': 'Status?', 'a': 'Sudah berhenti'},
            {'q': 'Alasan?', 'a': 'Pindah rumah'}
        ],
        "expected": "TIDAK TERTARIK"
    },
    {
        "name": "Tidak Butuh Internet (Strong Rejection)",
        "conversation": [
            {'q': 'Greeting?', 'a': 'Ya, benar'},
            {'q': 'Status?', 'a': 'Sudah berhenti'},
            {'q': 'Alasan?', 'a': 'Tidak butuh internet'}
        ],
        "expected": "TIDAK TERTARIK"
    },
    {
        "name": "Alasan Keuangan (Soft Rejection)",
        "conversation": [
            {'q': 'Greeting?', 'a': 'Ya, benar'},
            {'q': 'Status?', 'a': 'Sudah berhenti'},
            {'q': 'Alasan?', 'a': 'Alasan keuangan'}
        ],
        "expected": "PERLU FOLLOW-UP"  # Bisa di-follow up dengan promo
    },
    {
        "name": "Ada Gangguan + Bersedia Lanjut (Interest)",
        "conversation": [
            {'q': 'Greeting?', 'a': 'Ya, benar'},
            {'q': 'Status?', 'a': 'Ada gangguan'},
            {'q': 'Bersedia lanjut?', 'a': 'Ya, bersedia'}
        ],
        "expected": "KEMUNGKINAN TERTARIK"
    },
    {
        "name": "Masih Aktif + Tertarik Promo (Strong Interest)",
        "conversation": [
            {'q': 'Greeting?', 'a': 'Ya, benar'},
            {'q': 'Status?', 'a': 'Masih aktif'},
            {'q': 'Promo?', 'a': 'Tertarik'},
            {'q': 'Payment?', 'a': 'Ya, mau bayar'}
        ],
        "expected": "BERHASIL REAKTIVASI"
    }
]

print("=" * 80)
print("COMPREHENSIVE WINBACK PREDICTION TEST")
print("=" * 80)

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"Test {i}: {test['name']}")
    print(f"{'='*80}")
    
    result = predict_winback_outcome(test['conversation'])
    
    print(f"  Expected: {test['expected']}")
    print(f"  Actual: {result['keputusan']}")
    print(f"  Probability: {result['probability']}%")
    print(f"  Alasan: {result['alasan']}")
    
    if result['keputusan'] == test['expected']:
        print(f"  ✅ PASSED")
        passed += 1
    else:
        print(f"  ❌ FAILED")
        failed += 1

print(f"\n{'='*80}")
print(f"SUMMARY: {passed}/{len(test_cases)} tests passed")
print(f"{'='*80}")

if failed == 0:
    print("🎉 ALL TESTS PASSED!")
else:
    print(f"⚠️ {failed} test(s) failed")
