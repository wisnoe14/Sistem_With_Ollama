"""
🧪 COMPREHENSIVE WINBACK FLOW TEST
Test semua 5 main flows sesuai business requirement
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from app.services.winback_services import generate_question

def test_flow(name: str, steps: list):
    """Test a specific flow with given steps"""
    print(f"\n{'='*80}")
    print(f"🧪 {name}")
    print('='*80)
    
    hist = []
    for i, (expected_goal, answer) in enumerate(steps, 1):
        q = generate_question(hist)
        actual_goal = q['goal']
        
        # Check if goal matches
        status = "✅" if actual_goal == expected_goal else "❌"
        print(f"{status} Step {i}: {actual_goal} (expected: {expected_goal})")
        
        if actual_goal != expected_goal:
            print(f"   ⚠️  MISMATCH! Expected {expected_goal} but got {actual_goal}")
            return False
        
        # Add to history
        hist.append({'q': q['question'], 'a': answer, 'goal': actual_goal})
    
    print(f"\n✅ {name} - PASSED")
    return True

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                   WINBACK FLOW COMPREHENSIVE TEST                         ║
║                     Testing All 5 Main Flows                              ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")
    
    results = []
    
    # Flow 1: gangguan → complaint_apology → complaint_resolution → program_confirmation → closing
    results.append(test_flow(
        "Flow 1: gangguan → complaint_apology → complaint_resolution → program_confirmation → closing",
        [
            ("greeting_identity", "Ya, benar"),
            ("service_status", "Ada gangguan"),
            ("complaint_apology", "Sudah pernah lapor"),
            ("complaint_resolution", "Sudah diperbaiki"),
            ("program_confirmation", "Ya, tertarik"),
            ("closing_thanks", "")
        ]
    ))
    
    # Flow 2: gangguan → complaint_apology → complaint_resolution → consideration_confirmation → closing
    results.append(test_flow(
        "Flow 2: gangguan → complaint_apology → complaint_resolution → consideration_confirmation → closing",
        [
            ("greeting_identity", "Ya, benar"),
            ("service_status", "Ada gangguan"),
            ("complaint_apology", "Sudah pernah lapor"),
            ("complaint_resolution", "Sudah diperbaiki"),
            ("program_confirmation", "Masih pertimbangkan"),
            ("consideration_confirmation", "Akan hubungi nanti"),
            ("closing_thanks", "")
        ]
    ))
    
    # Flow 3: sudah berhenti → reason_inquiry → closing
    results.append(test_flow(
        "Flow 3: sudah berhenti → reason_inquiry → closing",
        [
            ("greeting_identity", "Ya, benar"),
            ("service_status", "Sudah berhenti"),
            ("reason_inquiry", "Pindah rumah"),
            ("closing", "")
        ]
    ))
    
    # Flow 4: masih aktif → promo → tertarik → payment → closing
    results.append(test_flow(
        "Flow 4: masih aktif → promo (tertarik) → payment → closing",
        [
            ("greeting_identity", "Ya, benar"),
            ("service_status", "Masih aktif"),
            ("promo_offer", "Tertarik"),
            ("payment_confirmation", "Besok"),
            ("closing", "")
        ]
    ))
    
    # Flow 5: masih aktif → promo → tidak tertarik → reason_inquiry → closing
    results.append(test_flow(
        "Flow 5: masih aktif → promo (tidak tertarik) → reason_inquiry → closing",
        [
            ("greeting_identity", "Ya, benar"),
            ("service_status", "Masih aktif"),
            ("promo_offer", "Tidak tertarik"),
            ("reason_inquiry", "Tidak butuh internet"),
            ("closing", "")
        ]
    ))
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print('='*80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if all(results):
        print("\n🎉 ALL TESTS PASSED! ✅")
        print("✨ Winback flow implementation is complete and working correctly!")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please check the output above for details.")
    
    print('='*80)

if __name__ == "__main__":
    main()
