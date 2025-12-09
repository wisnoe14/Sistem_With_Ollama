"""
Test Reason Generation dengan Ollama
=====================================
Test untuk memvalidasi bahwa fungsi generate_reason_with_ollama
menghasilkan alasan naratif yang koheren tanpa persentase.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import (
    predict_telecollection_outcome,
    predict_winback_outcome,
    predict_conversation_outcome
)

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_telecollection_reason():
    """Test reason generation untuk telecollection"""
    print_section("TEST TELECOLLECTION REASON GENERATION")
    
    # Test case 1: Customer dengan komitmen kuat
    print("\n📝 Test Case 1: Customer dengan komitmen timeline kuat")
    conversation_1 = [
        {"q": "Halo, untuk pembayaran ICONNET bulan ini sudah diselesaikan belum?", 
         "a": "Belum, maaf lupa", 
         "goal": "status_contact"},
        {"q": "Ada kendala yang membuat pembayaran tertunda?", 
         "a": "Belum ada waktu ke bank", 
         "goal": "payment_barrier"},
        {"q": "Kapan bisa diselesaikan pembayarannya?", 
         "a": "Besok pagi saya langsung bayar", 
         "goal": "payment_timeline"}
    ]
    
    result_1 = predict_telecollection_outcome(conversation_1)
    print(f"Keputusan: {result_1['keputusan']}")
    print(f"Confidence: {result_1['confidence']}")
    print(f"Probability: {result_1['probability']}%")
    print(f"\nALASAN:")
    print(f"{result_1['alasan']}")
    
    # Validate: tidak boleh ada persentase dalam alasan
    assert "%" not in result_1['alasan'], "❌ Alasan masih mengandung persentase!"
    assert len(result_1['alasan']) > 50, "❌ Alasan terlalu pendek!"
    print("\n✅ Alasan valid: naratif, tanpa persentase, koheren")
    
    # Test case 2: Customer dengan banyak kendala
    print("\n\n📝 Test Case 2: Customer dengan kendala berat")
    conversation_2 = [
        {"q": "Halo, untuk pembayaran ICONNET bulan ini sudah diselesaikan belum?", 
         "a": "Belum bisa bayar", 
         "goal": "status_contact"},
        {"q": "Ada kendala yang membuat pembayaran tertunda?", 
         "a": "Belum gajian, lagi susah uang", 
         "goal": "payment_barrier"},
        {"q": "Kapan bisa diselesaikan pembayarannya?", 
         "a": "Ga tahu, tunggu gajian dulu", 
         "goal": "payment_timeline"}
    ]
    
    result_2 = predict_telecollection_outcome(conversation_2)
    print(f"Keputusan: {result_2['keputusan']}")
    print(f"Confidence: {result_2['confidence']}")
    print(f"Probability: {result_2['probability']}%")
    print(f"\nALASAN:")
    print(f"{result_2['alasan']}")
    
    assert "%" not in result_2['alasan'], "❌ Alasan masih mengandung persentase!"
    assert len(result_2['alasan']) > 50, "❌ Alasan terlalu pendek!"
    print("\n✅ Alasan valid: naratif, tanpa persentase, koheren")
    
    print("\n\n✅ TELECOLLECTION REASON GENERATION - ALL TESTS PASSED!")

def test_winback_reason():
    """Test reason generation untuk winback"""
    print_section("TEST WINBACK REASON GENERATION")
    
    # Test case 1: Customer tertarik reaktivasi
    print("\n📝 Test Case 1: Customer tertarik reaktivasi")
    conversation_1 = [
        {"q": "Hai, selamat pagi. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak Ahmad?", 
         "a": "Ya, benar", 
         "goal": "greeting_identity"},
        {"q": "Baik Bapak/Ibu. Kami melihat bahwa layanan ICONNET Bapak/Ibu sedang terputus dan kami ingin tahu apakah ada kendala yang bisa kami bantu?", 
         "a": "Tidak ada gangguan, hanya belum bayar", 
         "goal": "service_status"},
        {"q": "Baik Bapak/Ibu, mohon maaf sebelumnya. Saat ini kami memiliki promo bayar 1 bulan gratis 1 bulan pemakaian. Bapak/Ibu, apakah tertarik?", 
         "a": "Tertarik, boleh deh", 
         "goal": "payment_status_info"}
    ]
    
    result_1 = predict_winback_outcome(conversation_1)
    print(f"Keputusan: {result_1['keputusan']}")
    print(f"Confidence: {result_1['confidence']}")
    print(f"Probability: {result_1['probability']}%")
    print(f"\nALASAN:")
    print(f"{result_1['alasan']}")
    
    assert "%" not in result_1['alasan'], "❌ Alasan masih mengandung persentase!"
    assert len(result_1['alasan']) > 50, "❌ Alasan terlalu pendek!"
    print("\n✅ Alasan valid: naratif, tanpa persentase, koheren")
    
    # Test case 2: Customer tidak tertarik
    print("\n\n📝 Test Case 2: Customer tidak tertarik reaktivasi")
    conversation_2 = [
        {"q": "Hai, selamat pagi. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak Ahmad?", 
         "a": "Ya, benar", 
         "goal": "greeting_identity"},
        {"q": "Baik Bapak/Ibu. Kami melihat bahwa layanan ICONNET Bapak/Ibu sedang terputus dan kami ingin tahu apakah ada kendala yang bisa kami bantu?", 
         "a": "Sudah berhenti", 
         "goal": "service_status"},
        {"q": "Baik Bapak/Ibu, jika boleh kami tahu berhentinya karena apa?", 
         "a": "Pindah rumah, sudah pakai provider lain", 
         "goal": "reason_inquiry"}
    ]
    
    result_2 = predict_winback_outcome(conversation_2)
    print(f"Keputusan: {result_2['keputusan']}")
    print(f"Confidence: {result_2['confidence']}")
    print(f"Probability: {result_2['probability']}%")
    print(f"\nALASAN:")
    print(f"{result_2['alasan']}")
    
    assert "%" not in result_2['alasan'], "❌ Alasan masih mengandung persentase!"
    assert len(result_2['alasan']) > 50, "❌ Alasan terlalu pendek!"
    print("\n✅ Alasan valid: naratif, tanpa persentase, koheren")
    
    print("\n\n✅ WINBACK REASON GENERATION - ALL TESTS PASSED!")

def test_retention_reason():
    """Test reason generation untuk retention"""
    print_section("TEST RETENTION REASON GENERATION")
    
    # Test case 1: Customer mau lanjut
    print("\n📝 Test Case 1: Customer mau lanjut berlangganan")
    conversation_1 = [
        {"q": "Selamat pagi, Bapak/Ibu. Perkenalkan saya Wisnu dari ICONNET. Apakah benar dengan Bapak Ahmad?", 
         "a": "Ya, benar dengan saya", 
         "goal": "greeting_identity"},
        {"q": "Baik Bapak, kami melihat layanan ICONNET Bapak sedang terputus. Apakah ada kendala yang bisa kami bantu?", 
         "a": "Iya memang sedang terputus", 
         "goal": "service_check"},
        {"q": "Boleh kami sampaikan ada promo diskon untuk reaktivasi?", 
         "a": "Boleh, silakan", 
         "goal": "promo_permission"},
        {"q": "Saat ini ada promo diskon 30% untuk 3 bulan pertama. Apakah Bapak tertarik untuk aktivasi kembali?", 
         "a": "Ya, tertarik. Saya mau lanjut", 
         "goal": "activation_interest"}
    ]
    
    result_1 = predict_conversation_outcome(conversation_1, "retention")
    print(f"Keputusan: {result_1['keputusan']}")
    print(f"Confidence: {result_1['confidence']}")
    print(f"Probability: {result_1['probability']}%")
    print(f"\nALASAN:")
    print(f"{result_1['alasan']}")
    
    assert "%" not in result_1['alasan'], "❌ Alasan masih mengandung persentase!"
    assert len(result_1['alasan']) > 50, "❌ Alasan terlalu pendek!"
    print("\n✅ Alasan valid: naratif, tanpa persentase, koheren")
    
    print("\n\n✅ RETENTION REASON GENERATION - ALL TESTS PASSED!")

if __name__ == "__main__":
    try:
        print("\n" + "="*70)
        print("  TEST REASON GENERATION DENGAN OLLAMA")
        print("  (Tanpa Persentase, Naratif Koheren)")
        print("="*70)
        
        test_telecollection_reason()
        test_winback_reason()
        test_retention_reason()
        
        print("\n" + "="*70)
        print("  ✅ ALL REASON GENERATION TESTS PASSED!")
        print("  Alasan sudah naratif, koheren, tanpa persentase")
        print("="*70 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
