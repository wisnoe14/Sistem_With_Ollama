#!/usr/bin/env python3
"""
Test untuk memastikan follow_up_plan goal tidak loop dan bisa progress
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import generate_question

def test_follow_up_goal_progression():
    """Test memastikan follow_up_plan goal bisa progress dengan proper"""
    print("🎯 TESTING FOLLOW_UP_PLAN GOAL PROGRESSION")
    print("=" * 60)
    
    # Simulate conversation yang sudah mencapai follow_up_plan stage
    conversation = [
        {"q": "Status pembayaran?", "a": "belum bayar", "goal": "status_contact"},
        {"q": "Ada kendala?", "a": "belum gajian", "goal": "payment_barrier"},  
        {"q": "Kapan bisa bayar?", "a": "tanggal 25", "goal": "payment_timeline"},
        {"q": "Metode pembayaran?", "a": "transfer bank", "goal": "payment_method"},
        {"q": "Komitmen bayar?", "a": "ya, pasti bayar", "goal": "commitment_confirm"},
    ]
    
    print(f"📋 Starting conversation with {len(conversation)} exchanges")
    
    # Test progression dari follow_up_plan beberapa kali
    for step in range(1, 5):
        print(f"\n🔄 Step {step}:")
        print("-" * 30)
        
        try:
            result = generate_question("telecollection", conversation)
            
            question = result.get('question', '')
            goal = result.get('goal', 'unknown')
            is_closing = result.get('is_closing', False)
            
            print(f"❓ Question: {question[:60]}{'...' if len(question) > 60 else ''}")
            print(f"🎯 Goal: {goal}")
            print(f"🔚 Is Closing: {is_closing}")
            
            # Simulate customer response untuk follow up questions
            if "follow up" in question.lower() or "diingatkan" in question.lower():
                if step == 1:
                    answer = "Ya, tolong diingatkan"
                elif step == 2:
                    answer = "Call H-1 ya"  
                elif step == 3:
                    answer = "WhatsApp aja"
                else:
                    answer = "Tidak perlu"
            else:
                answer = "Baik"
            
            # Add to conversation dengan goal field
            conversation.append({
                "q": question,
                "a": answer,
                "goal": goal
            })
            
            print(f"📝 Customer Answer: {answer}")
            
            # Check for progression
            if is_closing:
                print(f"✅ CONVERSATION COMPLETED at step {step}")
                break
                
            if goal != "follow_up_plan" and step > 1:
                print(f"✅ GOAL PROGRESSION: Moved away from follow_up_plan to '{goal}'")
                break
                
        except Exception as e:
            print(f"❌ ERROR at step {step}: {e}")
            break
    
    # Final analysis
    recent_goals = [conv.get('goal') for conv in conversation[-3:]]
    follow_up_count = recent_goals.count('follow_up_plan')
    
    print(f"\n📊 RESULTS:")
    print(f"✅ Total Exchanges: {len(conversation)}")
    print(f"✅ Recent Goals: {recent_goals}")
    print(f"✅ Follow_up_plan in last 3: {follow_up_count}")
    
    success = follow_up_count <= 2  # Allow max 2 follow_up attempts
    print(f"🎉 SUCCESS: {'PASS' if success else 'FAIL'}")
    
    return success

if __name__ == "__main__":
    print("🚀 TESTING FOLLOW_UP_PLAN PROGRESSION FIX")
    print("=" * 70)
    
    success = test_follow_up_goal_progression()
    
    print(f"\n{'='*70}")
    print("🏁 FINAL RESULT")
    print(f"{'='*70}")
    print(f"{'✅ FOLLOW_UP_PLAN PROGRESSION: WORKING!' if success else '❌ Still has issues'}")