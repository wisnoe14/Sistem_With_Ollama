import sys
sys.path.append('backend')

from app.services.gpt_service import check_conversation_goals, generate_question

# Test full conversation flow
conversation_history = [
    {
        "q": "Halo Budi, selamat pagi! Saya Wisnu dari ICONNET. Gimana kabarnya hari ini? Oh iya, saya mau tanya nih, untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?",
        "a": "Belum bayar"
    },
    {
        "q": "Halo! Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?",
        "a": "Belum bayar"  
    },
    {
        "q": "Saya ingin memahami situasinya - ada kendala khusus yang membuat pembayaran tertunda?",
        "a": "Belum gajian"
    }
]

print("=== TESTING NEXT QUESTION GENERATION ===")

# Test goal checking
goal_status = check_conversation_goals(conversation_history)
print(f"\n🎯 Current Goal Status:")
print(f"   Progress: {goal_status.get('achievement_percentage', 0)}%")
print(f"   Achieved: {goal_status.get('achieved_goals', [])}")
print(f"   Missing: {goal_status.get('missing_goals', [])}")

# Test next question generation
print(f"\n❓ Next Question Generation:")
result = generate_question("telecollection", conversation_history)
print(f"   Question: {result.get('question', 'No question')}")
print(f"   Goal: {result.get('goal', 'No goal')}")
print(f"   Options: {result.get('options', [])}")
print(f"   Is Closing: {result.get('is_closing', False)}")

print(f"\n🎯 Expected: Should generate payment_timeline question")