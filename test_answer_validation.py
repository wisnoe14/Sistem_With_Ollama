import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.goal_utils import check_conversation_goals
from app.services.telecollection_services import generate_question

print("=== TESTING ANSWER VALIDATION ISSUE ===")
print("Problem: When user gives answer outside options, conversation loops")

# Scenario 1: User gives valid option answer
print("\n1. SCENARIO 1: Valid option answer")
conversation_valid = [
    {
        "q": "Halo! Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?",
        "a": "Belum bayar"
    },
    {
        "q": "Saya ingin memahami situasinya - ada kendala khusus yang membuat pembayaran tertunda?",
        "a": "Belum gajian"  # Valid option
    }
]

goal_status = check_conversation_goals(conversation_valid)
next_question = generate_question(conversation_valid)
print(f"   Goals achieved: {goal_status.get('achieved_goals', [])}")
print(f"   Next question goal: {next_question.get('goal', 'No goal')}")
print(f"   Progress: {goal_status.get('achievement_percentage', 0):.1f}%")

# Scenario 2: User gives answer NOT in options
print("\n2. SCENARIO 2: Answer outside options (should cause loop)")
conversation_invalid = [
    {
        "q": "Halo! Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?",
        "a": "Belum bayar"
    },
    {
        "q": "Saya ingin memahami situasinya - ada kendala khusus yang membuat pembayaran tertunda?",
        "a": "Saya sibuk kerja"  # NOT in options: ["Belum gajian", "Uang lagi habis", "Ada keperluan mendesak", "Lupa jadwal bayar"]
    }
]

goal_status2 = check_conversation_goals(conversation_invalid)
next_question2 = generate_question(conversation_invalid)
print(f"   Goals achieved: {goal_status2.get('achieved_goals', [])}")
print(f"   Next question goal: {next_question2.get('goal', 'No goal')}")
print(f"   Progress: {goal_status2.get('achievement_percentage', 0):.1f}%")

print("\n3. EXPECTED BEHAVIOR:")
print("   - Answer 'Saya sibuk kerja' should still satisfy payment_barrier goal")
print("   - Should progress to payment_timeline, not loop on payment_barrier")
print("   - System should accept any reasonable answer, not just exact options")

# Scenario 3: Multiple invalid answers
print("\n4. SCENARIO 3: Multiple non-option answers")
conversation_multiple = [
    {
        "q": "Halo! Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?",
        "a": "Maaf belum sempat"  # NOT exact option
    },
    {
        "q": "Saya ingin memahami situasinya - ada kendala khusus yang membuat pembayaran tertunda?",
        "a": "Lagi ada masalah keluarga"  # NOT in options
    },
    {
        "q": "Kapan kira-kira bisa diselesaikan?",
        "a": "Insya Allah minggu depan"  # NOT exact option
    }
]

goal_status3 = check_conversation_goals(conversation_multiple)
print(f"   Goals achieved: {goal_status3.get('achieved_goals', [])}")
print(f"   Progress: {goal_status3.get('achievement_percentage', 0):.1f}%")

print(f"\n5. PROBLEM ANALYSIS:")
print("   Current system only validates answers that exactly match sentiment analysis")
print("   Need to improve answer validation to accept similar meanings, not just exact patterns")