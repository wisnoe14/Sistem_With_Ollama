"""
Test script untuk memverifikasi tampilan kendala dengan format natural (bukan mentah)
"""
import requests
import json

API_URL = "http://localhost:8000/api/v1/conversation/predict"

def test_barrier_natural_format():
    """Test apakah kendala ditampilkan dalam format natural yang mengalir"""
    
    print("\n" + "="*70)
    print("TEST: Natural Barrier Format in Alasan")
    print("="*70)
    
    test_cases = [
        {
            "name": "Kendala Finansial & Timing",
            "conversation": [
                {
                    "q": "Selamat siang Pak, ini dari ICONNET. Tagihan Bapak sudah jatuh tempo, apakah sudah ada rencana pembayaran?",
                    "a": "Oh iya, saya mau bayar tapi lagi ada masalah finansial. Gaji bulan ini belum cair."
                },
                {
                    "q": "Baik Pak, saya mengerti. Kira-kira kapan gaji Bapak cair?",
                    "a": "Biasanya tanggal 5, tapi bulan ini delay. Belum ada uang untuk bayar sekarang."
                }
            ],
            "expected_keywords": ["finansial", "kendala finansial", "keuangan"]
        },
        {
            "name": "Kendala Kesibukan",
            "conversation": [
                {
                    "q": "Pak, tagihan Bapak sudah jatuh tempo. Kapan bisa dilakukan pembayaran?",
                    "a": "Aduh maaf, saya lagi sibuk banget minggu ini. Belum sempat ke ATM."
                },
                {
                    "q": "Baik Pak, kalau begitu kapan Bapak ada waktu luang?",
                    "a": "Mungkin akhir minggu baru ada waktu. Sekarang meeting terus."
                }
            ],
            "expected_keywords": ["sibuk", "kesibukan", "tidak sempat"]
        },
        {
            "name": "Kendala Teknis",
            "conversation": [
                {
                    "q": "Pak, untuk pembayaran tagihan bulan ini bagaimana?",
                    "a": "Saya sudah coba bayar kemarin tapi ATM nya error terus."
                },
                {
                    "q": "Baik Pak, apakah sudah dicoba lagi atau ada cara pembayaran lain?",
                    "a": "Belum coba lagi sih, tadi sistemnya bermasalah."
                }
            ],
            "expected_keywords": ["teknis", "kendala teknis", "sistem"]
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST CASE {i}: {test_case['name']}")
        print(f"{'='*70}")
        
        payload = {
            "customer_id": f"TEST{i:03d}",
            "customer_name": f"Test Customer {i}",
            "topic": "telecollection",
            "conversation": test_case['conversation']
        }
        
        print(f"\n📤 Sending request...")
        print(f"   Conversation turns: {len(test_case['conversation'])}")
        
        try:
            response = requests.post(API_URL, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                alasan = result.get('frontend_result', {}).get('alasan', '')
                keputusan = result.get('frontend_result', {}).get('keputusan', 'N/A')
                
                print(f"\n📊 Result:")
                print(f"   Keputusan: {keputusan}")
                print(f"\n📝 Alasan (Natural Format):")
                print(f"   {alasan}")
                
                # Check if any expected keywords present
                found_keywords = [kw for kw in test_case['expected_keywords'] if kw.lower() in alasan.lower()]
                
                print(f"\n✅ Verifikasi:")
                
                # Check 1: Tidak ada tanda kutip mentah
                has_quotes = '"""' in alasan or '"' in alasan
                if not has_quotes:
                    print(f"   ✓ Tidak ada kutipan mentah dari jawaban user")
                else:
                    print(f"   ✗ GAGAL: Masih ada kutipan mentah")
                    all_passed = False
                
                # Check 2: Format natural (mengandung kata kunci yang diharapkan)
                if found_keywords:
                    print(f"   ✓ Format natural terdeteksi: {', '.join(found_keywords)}")
                else:
                    print(f"   ⚠ Kata kunci tidak ditemukan (expected: {test_case['expected_keywords']})")
                
                # Check 3: Alasan mengalir (panjang minimal 50 karakter, tidak terlalu pendek)
                if len(alasan) > 50:
                    print(f"   ✓ Alasan cukup lengkap ({len(alasan)} karakter)")
                else:
                    print(f"   ✗ GAGAL: Alasan terlalu pendek")
                    all_passed = False
                
            else:
                print(f"\n❌ Error: Status code {response.status_code}")
                print(f"   Response: {response.text}")
                all_passed = False
                
        except requests.exceptions.Timeout:
            print(f"\n❌ Request timeout")
            all_passed = False
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            all_passed = False
    
    print(f"\n{'='*70}")
    return all_passed


if __name__ == "__main__":
    print("\n🚀 Starting natural barrier format test...")
    print("⚠️  Make sure FastAPI server is running on localhost:8000")
    
    success = test_barrier_natural_format()
    
    if success:
        print("\n✅ All tests passed! Barriers displayed in natural format.")
    else:
        print("\n❌ Some tests failed!")

