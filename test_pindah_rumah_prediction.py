"""
Test prediction untuk case "Pindah rumah"
Seharusnya return TIDAK TERTARIK, bukan PERLU FOLLOW-UP
"""
from backend.app.services.gpt_service import predict_winback_outcome

# Test case: sudah berhenti → reason_inquiry (Pindah rumah)
conversation = [
    {'q': 'Selamat pagi, Bapak/Ibu. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Budi?', 'a': 'Ya, benar'},
    {'q': 'Baik Bapak/Ibu, kami melihat bahwa layanan Iconnet Bapak/Ibu sedang terputus. Kami ingin tahu apakah ada kendala yang bisa kami bantu?', 'a': 'Sudah berhenti'},
    {'q': 'Boleh tahu alasan Bapak/Ibu berhenti berlangganan atau tidak berminat dengan promo kami?', 'a': 'Pindah rumah'}
]

print("=" * 70)
print("TEST: Pindah Rumah Prediction")
print("=" * 70)

result = predict_winback_outcome(conversation)

print(f"\n📊 PREDICTION RESULT:")
print(f"  Status Dihubungi: {result['status_dihubungi']}")
print(f"  Keputusan: {result['keputusan']}")
print(f"  Probability: {result['probability']}%")
print(f"  Confidence: {result['confidence']}")
print(f"  Alasan: {result['alasan']}")

print(f"\n📈 DETAIL ANALYSIS:")
for key, value in result['detail_analysis'].items():
    print(f"  {key}: {value}")

print(f"\n✅ EXPECTED: TIDAK TERTARIK (bukan PERLU FOLLOW-UP)")
print(f"🎯 ACTUAL: {result['keputusan']}")

if result['keputusan'] == 'TIDAK TERTARIK':
    print(f"\n✅ SUCCESS: Prediction correct!")
else:
    print(f"\n❌ FAILED: Expected TIDAK TERTARIK, got {result['keputusan']}")
