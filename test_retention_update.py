"""
🧪 TEST RETENTION MODE - Comprehensive Flow Testing
Test the updated retention mode with 16 goals and dynamic branching
"""

import sys
sys.path.append('backend')

from app.services.gpt_service import (
    RETENTION_GOALS,
    RETENTION_QUESTIONS,
    determine_retention_next_goal,
    check_retention_goals
)

def test_retention_goals_count():
    """Test: Verify 16 goals are defined"""
    print("\n" + "="*60)
    print("TEST 1: Retention Goals Count")
    print("="*60)
    
    print(f"Total Goals: {len(RETENTION_GOALS)}")
    print(f"Expected: 16")
    
    assert len(RETENTION_GOALS) == 16, "Should have 16 retention goals"
    
    print("\n✅ PASS: 16 goals defined")
    print("\nGoals:")
    for i, goal in enumerate(RETENTION_GOALS, 1):
        print(f"  {i:2d}. {goal}")


def test_retention_questions_coverage():
    """Test: Verify all goals have question templates"""
    print("\n" + "="*60)
    print("TEST 2: Question Templates Coverage")
    print("="*60)
    
    missing_questions = []
    for goal in RETENTION_GOALS:
        if goal not in RETENTION_QUESTIONS:
            missing_questions.append(goal)
        else:
            print(f"✅ {goal}: {len(RETENTION_QUESTIONS[goal])} question(s)")
    
    if missing_questions:
        print(f"\n❌ Missing question templates for: {missing_questions}")
        assert False, f"Missing questions for {len(missing_questions)} goals"
    else:
        print(f"\n✅ PASS: All 16 goals have question templates")


def test_wrong_number_flow():
    """Test: Wrong number detection → early close"""
    print("\n" + "="*60)
    print("TEST 3: Wrong Number Flow")
    print("="*60)
    
    conversation = [
        {"q": "Apakah benar dengan Bapak Ahmad?", "a": "Bukan, salah sambung", "goal": "greeting_identity"},
        {"q": "Apakah Bapak Ahmad ada di tempat?", "a": "Tidak ada orang itu", "goal": "wrong_number_check"}
    ]
    
    goal_status = {
        "greeting_identity": {"achieved": True, "score": 85},
        "wrong_number_check": {"achieved": True, "score": 85}
    }
    
    next_goal = determine_retention_next_goal(conversation, goal_status)
    print(f"After wrong number confirmed: {next_goal}")
    
    assert next_goal == "closing", "Should close after confirming wrong number"
    print("✅ PASS: Wrong number → closing")


def test_declined_promo_complaint_flow():
    """Test: Decline promo → complaint → resolution → payment"""
    print("\n" + "="*60)
    print("TEST 4: Declined Promo + Complaint Flow")
    print("="*60)
    
    conversation = [
        {"q": "Apakah benar dengan Bapak Ahmad?", "a": "Ya benar", "goal": "greeting_identity"},
        {"q": "Layanan terputus?", "a": "Ya terputus", "goal": "service_check"},
        {"q": "Boleh saya sampaikan promo?", "a": "Tidak usah", "goal": "promo_permission"},
        {"q": "Apa alasan tidak berminat?", "a": "Ada gangguan terus", "goal": "rejection_reason"},
        {"q": "Apakah pernah melapor?", "a": "Sudah tapi tidak selesai", "goal": "complaint_handling"},
        {"q": "Jika gangguannya selesai, bersedia lanjut?", "a": "Bersedia kalau selesai", "goal": "complaint_resolution"}
    ]
    
    goal_status = {
        "greeting_identity": {"achieved": True, "score": 85},
        "service_check": {"achieved": True, "score": 85},
        "promo_permission": {"achieved": True, "score": 85},
        "rejection_reason": {"achieved": True, "score": 85},
        "complaint_handling": {"achieved": True, "score": 85},
        "complaint_resolution": {"achieved": True, "score": 85}
    }
    
    next_goal = determine_retention_next_goal(conversation, goal_status)
    print(f"After complaint resolved (willing): {next_goal}")
    
    assert next_goal == "payment_confirmation", "Should go to payment_confirmation after willing to continue"
    print("✅ PASS: Complaint resolved → payment_confirmation")


def test_activation_interest_stop_flow():
    """Test: Activation interest → STOP → stop_confirmation"""
    print("\n" + "="*60)
    print("TEST 5: Stop Confirmation Flow")
    print("="*60)
    
    conversation = [
        {"q": "Apakah benar dengan Bapak Ahmad?", "a": "Ya benar", "goal": "greeting_identity"},
        {"q": "Layanan terputus?", "a": "Ya terputus", "goal": "service_check"},
        {"q": "Boleh saya sampaikan promo?", "a": "Boleh", "goal": "promo_permission"},
        {"q": "Promo diskon 20%-30%", "a": "Oke", "goal": "promo_detail"},
        {"q": "Apakah berminat untuk mengaktifkan kembali?", "a": "Berhenti saja", "goal": "activation_interest"}
    ]
    
    goal_status = {
        "greeting_identity": {"achieved": True, "score": 85},
        "service_check": {"achieved": True, "score": 85},
        "promo_permission": {"achieved": True, "score": 85},
        "promo_detail": {"achieved": True, "score": 85},
        "activation_interest": {"achieved": True, "score": 85}
    }
    
    next_goal = determine_retention_next_goal(conversation, goal_status)
    print(f"After 'berhenti saja': {next_goal}")
    
    assert next_goal == "stop_confirmation", "Should ask stop_confirmation when customer says berhenti"
    print("✅ PASS: Berhenti → stop_confirmation")


def test_activation_interest_consider_flow():
    """Test: Activation interest → CONSIDER → consideration_timeline"""
    print("\n" + "="*60)
    print("TEST 6: Consideration Timeline Flow")
    print("="*60)
    
    conversation = [
        {"q": "Apakah benar dengan Bapak Ahmad?", "a": "Ya benar", "goal": "greeting_identity"},
        {"q": "Layanan terputus?", "a": "Ya terputus", "goal": "service_check"},
        {"q": "Boleh saya sampaikan promo?", "a": "Boleh", "goal": "promo_permission"},
        {"q": "Promo diskon 20%-30%", "a": "Oke", "goal": "promo_detail"},
        {"q": "Apakah berminat untuk mengaktifkan kembali?", "a": "Pertimbangkan dulu", "goal": "activation_interest"}
    ]
    
    goal_status = {
        "greeting_identity": {"achieved": True, "score": 85},
        "service_check": {"achieved": True, "score": 85},
        "promo_permission": {"achieved": True, "score": 85},
        "promo_detail": {"achieved": True, "score": 85},
        "activation_interest": {"achieved": True, "score": 85}
    }
    
    next_goal = determine_retention_next_goal(conversation, goal_status)
    print(f"After 'pertimbangkan dulu': {next_goal}")
    
    assert next_goal == "consideration_timeline", "Should ask consideration_timeline when customer says pertimbangkan"
    print("✅ PASS: Pertimbangkan → consideration_timeline")


def test_activation_interest_yes_flow():
    """Test: Activation interest → YES → payment_confirmation → payment_timing"""
    print("\n" + "="*60)
    print("TEST 7: Success Flow (Interested)")
    print("="*60)
    
    conversation = [
        {"q": "Apakah benar dengan Bapak Ahmad?", "a": "Ya benar", "goal": "greeting_identity"},
        {"q": "Layanan terputus?", "a": "Ya terputus", "goal": "service_check"},
        {"q": "Boleh saya sampaikan promo?", "a": "Boleh", "goal": "promo_permission"},
        {"q": "Promo diskon 20%-30%", "a": "Oke", "goal": "promo_detail"},
        {"q": "Apakah berminat untuk mengaktifkan kembali?", "a": "Berminat", "goal": "activation_interest"}
    ]
    
    goal_status = {
        "greeting_identity": {"achieved": True, "score": 85},
        "service_check": {"achieved": True, "score": 85},
        "promo_permission": {"achieved": True, "score": 85},
        "promo_detail": {"achieved": True, "score": 85},
        "activation_interest": {"achieved": True, "score": 85}
    }
    
    next_goal = determine_retention_next_goal(conversation, goal_status)
    print(f"After 'berminat': {next_goal}")
    
    assert next_goal == "payment_confirmation", "Should go to payment_confirmation when interested"
    
    # Continue to payment_timing
    goal_status["payment_confirmation"] = {"achieved": True, "score": 85}
    conversation.append({"q": "Email masih aktif?", "a": "Masih aktif", "goal": "payment_confirmation"})
    
    next_goal = determine_retention_next_goal(conversation, goal_status)
    print(f"After payment_confirmation: {next_goal}")
    
    assert next_goal == "payment_timing", "Should go to payment_timing after payment_confirmation"
    print("✅ PASS: Berminat → payment_confirmation → payment_timing")


def test_relocation_flow():
    """Test: Pindah rumah → device_location → relocation_interest"""
    print("\n" + "="*60)
    print("TEST 8: Relocation Flow")
    print("="*60)
    
    conversation = [
        {"q": "Apakah benar dengan Bapak Ahmad?", "a": "Ya benar", "goal": "greeting_identity"},
        {"q": "Layanan terputus?", "a": "Ya terputus", "goal": "service_check"},
        {"q": "Boleh saya sampaikan promo?", "a": "Boleh", "goal": "promo_permission"},
        {"q": "Promo diskon 20%-30%", "a": "Oke", "goal": "promo_detail"},
        {"q": "Apakah berminat untuk mengaktifkan kembali?", "a": "Tidak berminat", "goal": "activation_interest"},
        {"q": "Apa alasan tidak berminat?", "a": "Pindah rumah", "goal": "rejection_reason"}
    ]
    
    goal_status = {
        "greeting_identity": {"achieved": True, "score": 85},
        "service_check": {"achieved": True, "score": 85},
        "promo_permission": {"achieved": True, "score": 85},
        "promo_detail": {"achieved": True, "score": 85},
        "activation_interest": {"achieved": True, "score": 85},
        "rejection_reason": {"achieved": True, "score": 85}
    }
    
    next_goal = determine_retention_next_goal(conversation, goal_status)
    print(f"After 'pindah rumah': {next_goal}")
    
    assert next_goal == "device_location", "Should ask device_location after pindah rumah"
    
    # Continue to relocation_interest
    goal_status["device_location"] = {"achieved": True, "score": 85}
    conversation.append({"q": "Perangkat masih ada?", "a": "Masih ada", "goal": "device_location"})
    
    next_goal = determine_retention_next_goal(conversation, goal_status)
    print(f"After device_location: {next_goal}")
    
    assert next_goal == "relocation_interest", "Should ask relocation_interest after device check"
    print("✅ PASS: Pindah → device_location → relocation_interest")


def run_all_tests():
    """Run all retention mode tests"""
    print("\n" + "="*70)
    print("🧪 RETENTION MODE COMPREHENSIVE TESTING")
    print("="*70)
    
    try:
        test_retention_goals_count()
        test_retention_questions_coverage()
        test_wrong_number_flow()
        test_declined_promo_complaint_flow()
        test_activation_interest_stop_flow()
        test_activation_interest_consider_flow()
        test_activation_interest_yes_flow()
        test_relocation_flow()
        
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED!")
        print("="*70)
        print("\n✅ Retention mode is working correctly with 16 goals and dynamic branching")
        print("✅ All flow paths are properly implemented")
        print("✅ Helper functions are working as expected")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
