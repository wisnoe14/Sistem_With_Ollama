#!/usr/bin/env python3
"""
Test untuk memastikan financial_capability loop issue teratasi
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import generate_question

def test_financial_capability_loop_fix():
    """Test memastikan financial_capability tidak loop"""
    print("💰 TESTING FINANCIAL_CAPABILITY LOOP FIX")
    print("=" * 60)
    
    # Simulate conversation yang sudah mencapai financial_capability stage
    conversation = [
        {"q": "Status pembayaran?", "a": "belum bayar", "goal": "status_contact"},
        {"q": "Ada kendala?", "a": "belum gajian", "goal": "payment_barrier"},  
        {"q": "Kapan bisa bayar?", "a": "tanggal 25", "goal": "payment_timeline"},
        {"q": "Metode pembayaran?", "a": "transfer bank", "goal": "payment_method"},
        {"q": "Komitmen bayar?", "a": "ya, pasti bayar", "goal": "commitment_confirm"},
        {"q": "Follow up?", "a": "ya tolong diingatkan", "goal": "follow_up_plan"},
    ]
    
    print(f"📋 Starting conversation with {len(conversation)} exchanges")
    print(f"📋 Testing financial_capability loop prevention...")
    
    # Test progression dari financial_capability beberapa kali  
    questions_generated = []
    goals_seen = []
    
    for step in range(1, 6):
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
            
            # Track questions and goals
            questions_generated.append(question)
            goals_seen.append(goal)
            
            # Check for loops
            if question in questions_generated[:-1]:  # Exclude current question
                print(f"❌ LOOP DETECTED! Question repeated: {question[:40]}...")
                return False
            
            # Simulate customer response untuk financial_capability questions
            if "finansial" in question.lower() or "keuangan" in question.lower() or "kemampuan" in question.lower():
                if step == 1:
                    answer = "Ada kemampuan"
                elif step == 2:
                    answer = "Tidak ada hambatan"  
                else:
                    answer = "Ya, mampu bayar"
            elif is_closing:
                answer = "Terima kasih"
                print(f"✅ CONVERSATION CLOSED at step {step}")
                break
            else:
                answer = "Baik"
            
            # Add to conversation dengan goal field
            conversation.append({
                "q": question,
                "a": answer,
                "goal": goal
            })
            
            print(f"📝 Customer Answer: {answer}")
            
            # Check for progression away from financial_capability
            if goal != "financial_capability" and step > 1:
                print(f"✅ GOAL PROGRESSION: Moved away from financial_capability to '{goal}'")
                break
                
        except Exception as e:
            print(f"❌ ERROR at step {step}: {e}")
            break
    
    # Final analysis
    fc_count = goals_seen.count('financial_capability')
    unique_questions = len(set(questions_generated))
    
    print(f"\n📊 RESULTS:")
    print(f"✅ Total Steps: {len(goals_seen)}")
    print(f"✅ Goals Seen: {goals_seen}")
    print(f"✅ Financial_capability count: {fc_count}")
    print(f"✅ Unique Questions: {unique_questions}/{len(questions_generated)}")
    
    success = fc_count <= 3 and unique_questions == len(questions_generated)  # No loops, max 3 FC attempts
    print(f"🎉 SUCCESS: {'PASS' if success else 'FAIL'}")
    
    return success

if __name__ == "__main__":
    print("🚀 TESTING FINANCIAL_CAPABILITY LOOP FIX")
    print("=" * 70)
    
    success = test_financial_capability_loop_fix()
    
    print(f"\n{'='*70}")
    print("🏁 FINAL RESULT")
    print(f"{'='*70}")
    print(f"{'✅ FINANCIAL_CAPABILITY LOOP: FIXED!' if success else '❌ Still has loop issues'}")