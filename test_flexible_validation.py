import sys
sys.path.append('backend')

from app.services.gpt_service import check_conversation_goals, generate_question, analyze_sentiment_and_intent

print("=== COMPREHENSIVE FLEXIBLE ANSWER VALIDATION TEST ===")
print("Testing improved system that accepts answers outside exact options")

def test_scenario(title, conversation_history):
    print(f"\n{title}")
    print("-" * 50)
    
    goal_status = check_conversation_goals(conversation_history)
    next_question = generate_question("telecollection", conversation_history)
    
    print(f"Goals achieved: {goal_status.get('achieved_goals', [])}")
    print(f"Progress: {goal_status.get('achievement_percentage', 0):.1f}%")
    print(f"Next goal: {next_question.get('goal', 'No goal')}")
    print(f"Is closing: {next_question.get('is_closing', False)}")
    
    if next_question.get('is_closing'):
        print("✅ CONVERSATION COMPLETED SUCCESSFULLY!")
    
    return goal_status, next_question

# Test 1: Answers exactly matching options
test_scenario("1. EXACT OPTION ANSWERS", [
    {"q": "Pembayaran sudah diselesaikan?", "a": "Belum bayar"},
    {"q": "Ada kendala pembayaran?", "a": "Belum gajian"},
    {"q": "Kapan bisa bayar?", "a": "Besok"}
])

# Test 2: Answers similar but NOT exact options
test_scenario("2. SIMILAR BUT NON-EXACT ANSWERS", [
    {"q": "Pembayaran sudah diselesaikan?", "a": "Maaf belum sempat"},
    {"q": "Ada kendala pembayaran?", "a": "Saya sibuk kerja"},
    {"q": "Kapan bisa bayar?", "a": "Insya Allah minggu depan"}
])

# Test 3: Very different answers (should still work with flexible system)
test_scenario("3. VERY DIFFERENT ANSWERS", [
    {"q": "Pembayaran sudah diselesaikan?", "a": "Belum ada waktu ke bank"},
    {"q": "Ada kendala pembayaran?", "a": "Lagi ada masalah keluarga yang mendesak"},
    {"q": "Kapan bisa bayar?", "a": "Setelah urusan ini selesai, mungkin akhir bulan"}
])

# Test 4: Mixed responses
test_scenario("4. MIXED RESPONSE QUALITY", [
    {"q": "Pembayaran sudah diselesaikan?", "a": "ya"},  # Short response
    {"q": "Ada kendala pembayaran?", "a": "Lagi repot dengan pekerjaan"},  # Detailed
    {"q": "Kapan bisa bayar?", "a": "hmm"}  # Very short
])

# Test 5: Payment completion during conversation
test_scenario("5. EARLY PAYMENT COMPLETION", [
    {"q": "Pembayaran sudah diselesaikan?", "a": "Belum bayar"},
    {"q": "Ada kendala pembayaran?", "a": "Oh tunggu, tadi sudah bayar sebenarnya"}
])

print(f"\n" + "="*60)
print("TEST SUMMARY:")
print("✅ System should now accept flexible answers")
print("✅ No more infinite loops on non-option answers")
print("✅ Progress should advance naturally through goals")
print("✅ Conversation should complete appropriately")