"""
Test Winback Script Alignment
================================
Test untuk memvalidasi bahwa winback flow sudah sesuai dengan script resmi.

Test 4 Branch:
1. Branch A: Sudah berhenti → reason → device → provider → stop confirmation → closing
2. Branch B: Ada gangguan → apology → resolution → (bersedia/pertimbang) → closing
3. Branch C: Tidak ada gangguan (unpaid) → payment status → promo → (tertarik/tidak) → closing
4. Branch D: Tidak respon → no response → closing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import (
    determine_winback_next_goal,
    check_winback_goals,
    WINBACK_QUESTIONS
)

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_branch_a_sudah_berhenti():
    """Test Branch A: Sudah berhenti"""
    print_section("TEST BRANCH A: SUDAH BERHENTI")
    
    conversation = [
        {"q": "Hai, selamat pagi. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Ahmad?", 
         "a": "Ya, benar", 
         "goal": "greeting_identity"},
        {"q": "Baik Bapak/Ibu. Kami melihat bahwa layanan ICONNET Bapak/Ibu sedang terputus dan kami ingin tahu apakah ada kendala yang bisa kami bantu?", 
         "a": "Sudah berhenti", 
         "goal": "service_status"},
    ]
    
    goal_status = check_winback_goals(conversation)
    
    # Test sequence: reason_inquiry
    next_goal = determine_winback_next_goal(conversation, goal_status)
    assert next_goal == "reason_inquiry", f"Expected 'reason_inquiry', got '{next_goal}'"
    print(f"✅ After 'Sudah berhenti' → next_goal = {next_goal}")
    
    # Add reason_inquiry
    conversation.append({
        "q": "Baik Bapak/Ibu, jika boleh kami tahu berhentinya karena apa?",
        "a": "Pindah rumah",
        "goal": "reason_inquiry"
    })
    goal_status = check_winback_goals(conversation)
    
    # Test sequence: device_check
    next_goal = determine_winback_next_goal(conversation, goal_status)
    assert next_goal == "device_check", f"Expected 'device_check', got '{next_goal}'"
    print(f"✅ After reason_inquiry → next_goal = {next_goal}")
    
    # Add device_check
    conversation.append({
        "q": "Untuk perangkat ICONNET-nya, apakah masih berada di lokasi?",
        "a": "Masih ada",
        "goal": "device_check"
    })
    goal_status = check_winback_goals(conversation)
    
    # Test sequence: current_provider
    next_goal = determine_winback_next_goal(conversation, goal_status)
    assert next_goal == "current_provider", f"Expected 'current_provider', got '{next_goal}'"
    print(f"✅ After device_check → next_goal = {next_goal}")
    
    # Add current_provider
    conversation.append({
        "q": "Untuk saat ini Bapak/Ibu menggunakan provider apa?",
        "a": "Provider lain",
        "goal": "current_provider"
    })
    goal_status = check_winback_goals(conversation)
    
    # Test sequence: stop_confirmation
    next_goal = determine_winback_next_goal(conversation, goal_status)
    assert next_goal == "stop_confirmation", f"Expected 'stop_confirmation', got '{next_goal}'"
    print(f"✅ After current_provider → next_goal = {next_goal}")
    
    # Add stop_confirmation
    conversation.append({
        "q": "Baik Bapak/Ibu, kami konfirmasi ulang bahwa Bapak/Ibu berhenti berlangganan ya. Terima kasih atas waktunya.",
        "a": "Ya, berhenti",
        "goal": "stop_confirmation"
    })
    goal_status = check_winback_goals(conversation)
    
    # Test sequence: closing_thanks
    next_goal = determine_winback_next_goal(conversation, goal_status)
    assert next_goal == "closing_thanks", f"Expected 'closing_thanks', got '{next_goal}'"
    print(f"✅ After stop_confirmation → next_goal = {next_goal}")
    
    print("\n✅ BRANCH A (SUDAH BERHENTI) - ALL TESTS PASSED!")

def test_branch_b_gangguan():
    """Test Branch B: Ada gangguan jaringan"""
    print_section("TEST BRANCH B: ADA GANGGUAN JARINGAN")
    
    conversation = [
        {"q": "Hai, selamat pagi. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Ahmad?", 
         "a": "Ya, benar", 
         "goal": "greeting_identity"},
        {"q": "Baik Bapak/Ibu. Kami melihat bahwa layanan ICONNET Bapak/Ibu sedang terputus dan kami ingin tahu apakah ada kendala yang bisa kami bantu?", 
         "a": "Ada gangguan jaringan", 
         "goal": "service_status"},
    ]
    
    goal_status = check_winback_goals(conversation)
    
    # Test sequence: complaint_apology
    next_goal = determine_winback_next_goal(conversation, goal_status)
    assert next_goal == "complaint_apology", f"Expected 'complaint_apology', got '{next_goal}'"
    print(f"✅ After 'Ada gangguan' → next_goal = {next_goal}")
    
    # Add complaint_apology
    conversation.append({
        "q": "Sebelumnya mohon maaf atas ketidaknyamanan Bapak/Ibu. Apakah Bapak/Ibu sudah pernah melaporkan gangguan sebelumnya?",
        "a": "Sudah pernah",
        "goal": "complaint_apology"
    })
    goal_status = check_winback_goals(conversation)
    
    # Test sequence: complaint_resolution
    next_goal = determine_winback_next_goal(conversation, goal_status)
    assert next_goal == "complaint_resolution", f"Expected 'complaint_resolution', got '{next_goal}'"
    print(f"✅ After complaint_apology → next_goal = {next_goal}")
    
    # Test Sub-branch B1: Bersedia lanjut
    print("\n--- Sub-branch B1: Bersedia lanjut ---")
    conversation_b1 = conversation.copy()
    conversation_b1.append({
        "q": "Baik, akan kami lakukan pengecekan ulang atas kendala tersebut Bapak/Ibu. Jika kendala sudah teratasi, apakah Bapak/Ibu bersedia lanjut berlangganan?",
        "a": "Bersedia lanjut",
        "goal": "complaint_resolution"
    })
    goal_status_b1 = check_winback_goals(conversation_b1)
    next_goal = determine_winback_next_goal(conversation_b1, goal_status_b1)
    assert next_goal == "program_confirmation", f"Expected 'program_confirmation', got '{next_goal}'"
    print(f"✅ After 'Bersedia lanjut' → next_goal = {next_goal}")
    
    # Test Sub-branch B2: Pertimbangkan dulu
    print("\n--- Sub-branch B2: Pertimbangkan dulu ---")
    conversation_b2 = conversation.copy()
    conversation_b2.append({
        "q": "Baik, akan kami lakukan pengecekan ulang atas kendala tersebut Bapak/Ibu. Jika kendala sudah teratasi, apakah Bapak/Ibu bersedia lanjut berlangganan?",
        "a": "Pertimbangkan dulu",
        "goal": "complaint_resolution"
    })
    goal_status_b2 = check_winback_goals(conversation_b2)
    next_goal = determine_winback_next_goal(conversation_b2, goal_status_b2)
    assert next_goal == "consideration_confirmation", f"Expected 'consideration_confirmation', got '{next_goal}'"
    print(f"✅ After 'Pertimbangkan' → next_goal = {next_goal}")
    
    # Test Sub-branch B3: Tidak berminat
    print("\n--- Sub-branch B3: Tidak berminat ---")
    conversation_b3 = conversation.copy()
    conversation_b3.append({
        "q": "Baik, akan kami lakukan pengecekan ulang atas kendala tersebut Bapak/Ibu. Jika kendala sudah teratasi, apakah Bapak/Ibu bersedia lanjut berlangganan?",
        "a": "Tidak berminat",
        "goal": "complaint_resolution"
    })
    goal_status_b3 = check_winback_goals(conversation_b3)
    next_goal = determine_winback_next_goal(conversation_b3, goal_status_b3)
    assert next_goal == "closing_thanks", f"Expected 'closing_thanks', got '{next_goal}'"
    print(f"✅ After 'Tidak berminat' → next_goal = {next_goal}")
    
    print("\n✅ BRANCH B (ADA GANGGUAN) - ALL TESTS PASSED!")

def test_branch_c_unpaid():
    """Test Branch C: Tidak ada gangguan (belum bayar)"""
    print_section("TEST BRANCH C: TIDAK ADA GANGGUAN (BELUM BAYAR)")
    
    conversation = [
        {"q": "Hai, selamat pagi. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Ahmad?", 
         "a": "Ya, benar", 
         "goal": "greeting_identity"},
        {"q": "Baik Bapak/Ibu. Kami melihat bahwa layanan ICONNET Bapak/Ibu sedang terputus dan kami ingin tahu apakah ada kendala yang bisa kami bantu?", 
         "a": "Tidak ada gangguan", 
         "goal": "service_status"},
    ]
    
    goal_status = check_winback_goals(conversation)
    
    # Test sequence: payment_status_info
    next_goal = determine_winback_next_goal(conversation, goal_status)
    assert next_goal == "payment_status_info", f"Expected 'payment_status_info', got '{next_goal}'"
    print(f"✅ After 'Tidak ada gangguan' → next_goal = {next_goal}")
    
    # Test Sub-branch C1: Tertarik dengan promo
    print("\n--- Sub-branch C1: Tertarik dengan promo ---")
    conversation_c1 = conversation.copy()
    conversation_c1.append({
        "q": "Baik Bapak/Ibu, mohon maaf sebelumnya. Nama pelanggan Bapak/Ibu tercantum pada sistem kami karena belum melakukan pembayaran. Saat ini kami memiliki promo bayar 1 bulan gratis 1 bulan pemakaian. Bapak/Ibu, apakah tertarik?",
        "a": "Tertarik",
        "goal": "payment_status_info"
    })
    goal_status_c1 = check_winback_goals(conversation_c1)
    next_goal = determine_winback_next_goal(conversation_c1, goal_status_c1)
    assert next_goal == "payment_timing", f"Expected 'payment_timing', got '{next_goal}'"
    print(f"✅ After 'Tertarik' → next_goal = {next_goal}")
    
    # Add payment_timing
    conversation_c1.append({
        "q": "Baik Bapak/Ibu, akan kami proses. Kalau boleh tahu, kapan akan dibayar?",
        "a": "Besok",
        "goal": "payment_timing"
    })
    goal_status_c1 = check_winback_goals(conversation_c1)
    next_goal = determine_winback_next_goal(conversation_c1, goal_status_c1)
    assert next_goal == "program_confirmation", f"Expected 'program_confirmation', got '{next_goal}'"
    print(f"✅ After payment_timing → next_goal = {next_goal}")
    
    # Test Sub-branch C2: Tidak tertarik
    print("\n--- Sub-branch C2: Tidak tertarik ---")
    conversation_c2 = conversation.copy()
    conversation_c2.append({
        "q": "Baik Bapak/Ibu, mohon maaf sebelumnya. Nama pelanggan Bapak/Ibu tercantum pada sistem kami karena belum melakukan pembayaran. Saat ini kami memiliki promo bayar 1 bulan gratis 1 bulan pemakaian. Bapak/Ibu, apakah tertarik?",
        "a": "Tidak tertarik",
        "goal": "payment_status_info"
    })
    goal_status_c2 = check_winback_goals(conversation_c2)
    next_goal = determine_winback_next_goal(conversation_c2, goal_status_c2)
    assert next_goal == "rejection_reason", f"Expected 'rejection_reason', got '{next_goal}'"
    print(f"✅ After 'Tidak tertarik' → next_goal = {next_goal}")
    
    # Test Sub-branch C3: Pertimbangkan dulu
    print("\n--- Sub-branch C3: Pertimbangkan dulu ---")
    conversation_c3 = conversation.copy()
    conversation_c3.append({
        "q": "Baik Bapak/Ibu, mohon maaf sebelumnya. Nama pelanggan Bapak/Ibu tercantum pada sistem kami karena belum melakukan pembayaran. Saat ini kami memiliki promo bayar 1 bulan gratis 1 bulan pemakaian. Bapak/Ibu, apakah tertarik?",
        "a": "Pertimbangkan dulu",
        "goal": "payment_status_info"
    })
    goal_status_c3 = check_winback_goals(conversation_c3)
    next_goal = determine_winback_next_goal(conversation_c3, goal_status_c3)
    assert next_goal == "closing_thanks", f"Expected 'closing_thanks', got '{next_goal}'"
    print(f"✅ After 'Pertimbangkan' → next_goal = {next_goal}")
    
    print("\n✅ BRANCH C (TIDAK ADA GANGGUAN/UNPAID) - ALL TESTS PASSED!")

def test_branch_d_no_response():
    """Test Branch D: Tidak respon"""
    print_section("TEST BRANCH D: TIDAK RESPON")
    
    conversation = [
        {"q": "Hai, selamat pagi. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Ahmad?", 
         "a": "Ya, benar", 
         "goal": "greeting_identity"},
        {"q": "Baik Bapak/Ibu. Kami melihat bahwa layanan ICONNET Bapak/Ibu sedang terputus dan kami ingin tahu apakah ada kendala yang bisa kami bantu?", 
         "a": "Tidak respon", 
         "goal": "service_status"},
    ]
    
    goal_status = check_winback_goals(conversation)
    
    # Test sequence: no_response
    next_goal = determine_winback_next_goal(conversation, goal_status)
    assert next_goal == "no_response", f"Expected 'no_response', got '{next_goal}'"
    print(f"✅ After 'Tidak respon' → next_goal = {next_goal}")
    
    # Add no_response
    conversation.append({
        "q": "Baik Bapak/Ibu, karena tidak ada respon kami tutup teleponnya. Mohon maaf mengganggu, terima kasih.",
        "a": "Selesai",
        "goal": "no_response"
    })
    goal_status = check_winback_goals(conversation)
    
    # Test sequence: closing_thanks
    next_goal = determine_winback_next_goal(conversation, goal_status)
    assert next_goal == "closing_thanks", f"Expected 'closing_thanks', got '{next_goal}'"
    print(f"✅ After no_response → next_goal = {next_goal}")
    
    print("\n✅ BRANCH D (TIDAK RESPON) - ALL TESTS PASSED!")

def test_winback_questions_structure():
    """Test struktur WINBACK_QUESTIONS sesuai script"""
    print_section("TEST WINBACK_QUESTIONS STRUCTURE")
    
    required_goals = [
        "greeting_identity",
        "service_status",
        "reason_inquiry",
        "device_check",
        "current_provider",
        "stop_confirmation",
        "complaint_apology",
        "complaint_resolution",
        "consideration_confirmation",
        "no_response",
        "payment_status_info",
        "payment_timing",
        "program_confirmation",
        "rejection_reason",
        "closing_thanks"
    ]
    
    print(f"Required goals: {len(required_goals)}")
    print(f"Available goals: {len(WINBACK_QUESTIONS)}")
    
    for goal in required_goals:
        assert goal in WINBACK_QUESTIONS, f"Missing goal: {goal}"
        assert len(WINBACK_QUESTIONS[goal]) > 0, f"Goal '{goal}' has no questions"
        print(f"✅ {goal}: {WINBACK_QUESTIONS[goal][0]['question'][:60]}...")
    
    print(f"\n✅ ALL {len(required_goals)} WINBACK GOALS VALIDATED!")

if __name__ == "__main__":
    try:
        print("\n" + "="*60)
        print("  WINBACK SCRIPT ALIGNMENT TEST")
        print("="*60)
        
        # Test struktur questions
        test_winback_questions_structure()
        
        # Test 4 branch utama
        test_branch_a_sudah_berhenti()
        test_branch_b_gangguan()
        test_branch_c_unpaid()
        test_branch_d_no_response()
        
        print("\n" + "="*60)
        print("  ✅ ALL WINBACK TESTS PASSED!")
        print("  Winback flow sudah sesuai dengan script resmi")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
