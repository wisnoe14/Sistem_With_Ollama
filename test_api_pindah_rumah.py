"""
Test API endpoint for winback prediction dengan case "Pindah rumah"
Verifikasi bahwa prediction sudah return TIDAK TERTARIK
"""
import requests
import json

API_BASE = "http://127.0.0.1:8000/api/v1/endpoints"

# Conversation history: sudah berhenti → Pindah rumah
conversation_history = [
        {
            "q": "Status Dihubungi?",
            "a": "Dihubungi"
        },
        {
            "q": "Selamat pagi, Bapak/Ibu. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Test Customer?",
            "a": "Ya, benar"
        },
        {
            "q": "Baik Bapak/Ibu, kami melihat bahwa layanan Iconnet Bapak/Ibu sedang terputus. Kami ingin tahu apakah ada kendala yang bisa kami bantu?",
            "a": "Sudah berhenti"
        },
        {
            "q": "Boleh tahu alasan Bapak/Ibu berhenti berlangganan atau tidak berminat dengan promo kami?",
            "a": "Pindah rumah"
        }
    ]

conversation_data = {
    "customer_id": "TEST_PINDAH",
    "mode": "winback",
    "topic": "winback",
    "cs_name": "Wisnu",
    "customer_name": "Test Customer",
    "time": "pagi",
    "conversation": conversation_history,  # Full history including status dihubungi
    "conversation_history": conversation_history[1:]  # Skip status dihubungi
}

print("=" * 80)
print("TEST: API Prediction untuk Pindah Rumah Case")
print("=" * 80)

try:
    response = requests.post(
        f"{API_BASE}/conversation/predict",
        json=conversation_data,
        timeout=10
    )
    
    if response.status_code == 200:
        response_data = response.json()
        result = response_data.get('result', response_data)  # Handle nested result
        
        print(f"\n📊 API RESPONSE:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        print(f"\n🎯 KEY FIELDS:")
        print(f"  Status: {result.get('status')}")
        print(f"  Keputusan: {result.get('keputusan')}")
        print(f"  Probability: {result.get('probability')}")
        print(f"  Confidence: {result.get('confidence')}")
        print(f"  Alasan: {result.get('alasan')}")
        
        print(f"\n✅ EXPECTED: Status = TIDAK TERTARIK")
        print(f"🎯 ACTUAL: Status = {result.get('status')}, Keputusan = {result.get('keputusan')}")
        
        if result.get('status') == 'TIDAK TERTARIK' or result.get('keputusan') == 'TIDAK TERTARIK':
            print(f"\n✅ SUCCESS: Prediction correct!")
        else:
            print(f"\n❌ FAILED: Expected TIDAK TERTARIK, got status={result.get('status')}, keputusan={result.get('keputusan')}")
    else:
        print(f"\n❌ API ERROR: Status {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print(f"\n⚠️ Connection Error: Make sure FastAPI server is running on {API_BASE}")
except Exception as e:
    print(f"\n❌ Error: {e}")
