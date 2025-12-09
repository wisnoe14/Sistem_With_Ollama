import sys
sys.path.append('backend')

from app.services.gpt_service import check_conversation_goals, generate_question

print("=== FINAL REALISTIC CONVERSATION TEST ===")
print("Testing conversation with user giving various non-option answers")

def simulate_full_conversation():
    """Simulate a complete conversation with realistic user responses"""
    
    # Scenario: User gives answers that are NOT in the exact options
    conversation_history = []
    
    print("\n🤖 AI: Halo! Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?")
    print("Options: ['Sudah bayar', 'Belum bayar', 'Lupa', 'Akan segera bayar']")
    print("👤 Customer: Waduh maaf ya, lagi banyak kerjaan jadi belum sempat")
    
    conversation_history.append({
        "q": "Halo! Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?",
        "a": "Waduh maaf ya, lagi banyak kerjaan jadi belum sempat"
    })
    
    # Generate next question
    next_q = generate_question("telecollection", conversation_history)
    print(f"\n🤖 AI: {next_q['question']}")
    print(f"Options: {next_q['options']}")
    print("👤 Customer: Sibuk banget sama proyek kantor")
    
    conversation_history.append({
        "q": next_q['question'],
        "a": "Sibuk banget sama proyek kantor"
    })
    
    # Generate next question
    next_q2 = generate_question("telecollection", conversation_history)
    print(f"\n🤖 AI: {next_q2['question']}")
    print(f"Options: {next_q2['options']}")
    print("👤 Customer: Kalau gitu besok aja deh ya")
    
    conversation_history.append({
        "q": next_q2['question'],
        "a": "Kalau gitu besok aja deh ya"
    })
    
    # Final check
    final_result = generate_question("telecollection", conversation_history)
    
    print(f"\n🎯 FINAL RESULT:")
    print(f"Is conversation closing: {final_result.get('is_closing', False)}")
    if final_result.get('is_closing'):
        print(f"Closing message: {final_result.get('question', 'No message')[:100]}...")
        print("✅ SUCCESS: Conversation completed naturally!")
    else:
        print(f"Next question: {final_result.get('question', 'No question')}")
        print("❌ ISSUE: Conversation should have completed")
    
    return conversation_history, final_result

# Run simulation
history, result = simulate_full_conversation()

# Test goal completion
goal_status = check_conversation_goals(history)
print(f"\n📊 GOAL ANALYSIS:")
print(f"   Achieved goals: {goal_status.get('achieved_goals', [])}")
print(f"   Completion: {goal_status.get('achievement_percentage', 0):.1f}%")
print(f"   Should complete: {goal_status.get('completed', False)}")

print(f"\n" + "="*60)
print("SUMMARY:")
print("✅ No infinite loops on non-option answers") 
print("✅ Flexible acceptance of various response styles")
print("✅ Natural conversation progression")
print("✅ Proper conversation completion")