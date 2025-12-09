import sys
sys.path.append('backend')

from app.services.gpt_service import predict_telecollection_outcome, generate_final_prediction

print("=== TESTING CURRENT PREDICTION SYSTEM ===")

# Test scenarios for prediction
test_scenarios = [
    {
        "name": "SCENARIO 1: Customer sudah bayar",
        "conversation": [
            {"q": "Pembayaran sudah diselesaikan?", "a": "Oh maaf, kemarin sudah bayar kok", "goal": "status_contact"}
        ]
    },
    {
        "name": "SCENARIO 2: Customer berkomitmen timeline jelas",
        "conversation": [
            {"q": "Pembayaran sudah diselesaikan?", "a": "Belum bayar", "goal": "status_contact"},
            {"q": "Ada kendala pembayaran?", "a": "Belum gajian", "goal": "payment_barrier"},
            {"q": "Kapan bisa bayar?", "a": "Besok pasti", "goal": "payment_timeline"}
        ]
    },
    {
        "name": "SCENARIO 3: Customer ada kendala tapi kasih timeline",
        "conversation": [
            {"q": "Pembayaran sudah diselesaikan?", "a": "Belum bayar", "goal": "status_contact"},
            {"q": "Ada kendala pembayaran?", "a": "Lagi susah, uang habis", "goal": "payment_barrier"},
            {"q": "Kapan bisa bayar?", "a": "Minggu depan mungkin", "goal": "payment_timeline"}
        ]
    },
    {
        "name": "SCENARIO 4: Customer banyak kendala, tidak berkomitmen",
        "conversation": [
            {"q": "Pembayaran sudah diselesaikan?", "a": "Belum bayar", "goal": "status_contact"},
            {"q": "Ada kendala pembayaran?", "a": "Lagi susah banget", "goal": "payment_barrier"},
            {"q": "Kapan bisa bayar?", "a": "Tidak tahu", "goal": "payment_timeline"}
        ]
    },
    {
        "name": "SCENARIO 5: Answers di luar opsi (yang sudah diperbaiki)",
        "conversation": [
            {"q": "Pembayaran sudah diselesaikan?", "a": "Waduh maaf ya, lagi banyak kerjaan jadi belum sempat", "goal": "status_contact"},
            {"q": "Ada kendala pembayaran?", "a": "Sibuk banget sama proyek kantor", "goal": "payment_barrier"},
            {"q": "Kapan bisa bayar?", "a": "Kalau gitu besok aja deh ya", "goal": "payment_timeline"}
        ]
    }
]

for scenario in test_scenarios:
    print(f"\n{scenario['name']}")
    print("-" * 60)
    
    # Test prediction
    prediction = predict_telecollection_outcome(scenario['conversation'])
    
    print(f"📊 PREDICTION RESULT:")
    print(f"   Status: {prediction.get('status_dihubungi', 'N/A')}")
    print(f"   Keputusan: {prediction.get('keputusan', 'N/A')}")
    print(f"   Probability: {prediction.get('probability', 0)}%")
    print(f"   Confidence: {prediction.get('confidence', 'N/A')}")
    print(f"   Alasan: {prediction.get('alasan', 'N/A')}")

print(f"\n" + "="*60)
print("ISSUES TO FIX:")
print("1. Prediksi mungkin tidak akurat untuk flexible answers")
print("2. Perlu lebih sophisticated scoring system")
print("3. Timeline commitment detection perlu diperbaiki")
print("4. Barrier severity assessment kurang detail")
print("5. Probability calculation bisa lebih nuanced")