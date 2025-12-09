import sys
sys.path.append('backend')

from app.services.gpt_service import check_conversation_goals, validate_goal_with_sentiment

# Test conversation history yang mencerminkan situasi saat ini
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

print("=== TESTING GOAL PROGRESSION ISSUE ===")
print(f"Conversation history: {len(conversation_history)} entries")

# Test individual goal validations
print(f"\n🔍 Individual Goal Validations:")
for i, goal in enumerate(['status_contact', 'payment_barrier', 'payment_timeline']):
    if i < len(conversation_history):
        answer = conversation_history[i]['a']
        validation = validate_goal_with_sentiment(goal, answer)
        print(f"   Goal '{goal}' with answer '{answer}' → Achieved: {validation['achieved']}")
    else:
        print(f"   Goal '{goal}' → No answer yet")

# Test overall goal checking
print(f"\n🎯 Overall Goal Status:")
goal_status = check_conversation_goals(conversation_history)
print(f"   Completed: {goal_status.get('completed', False)}")
print(f"   Progress: {goal_status.get('achievement_percentage', 0)}%")
print(f"   Achieved: {goal_status.get('achieved_goals', [])}")
print(f"   Missing: {goal_status.get('missing_goals', [])}")

# Check each goal result detail
print(f"\n📊 Goal Details:")
for goal in ['status_contact', 'payment_barrier', 'payment_timeline']:
    if goal in goal_status:
        result = goal_status[goal]
        print(f"   {goal}: {result}")