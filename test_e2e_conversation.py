#!/usr/bin/env python3
"""
Test comprehensive end-to-end conversation flow untuk memastikan sistem menggali semua goals
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import generate_question

def test_end_to_end_conversation():
    """Test conversation flow dari awal sampai semua goals tercapai"""
    print("🎯 TESTING END-TO-END CONVERSATION FLOW")
    print("=" * 60)
    
    # Test telecollection conversation yang menggali semua goals
    print(f"\n📋 TESTING TELECOLLECTION - FULL CONVERSATION")
    print("=" * 50)
    
    conversation = []
    max_questions = 10
    
    for step in range(1, max_questions + 1):
        print(f"\n🔄 Step {step}:")
        print("-" * 20)
        
        try:
            result = generate_question("telecollection", conversation)
            
            # Show question generated
            question = result.get('question', 'N/A')
            goal = result.get('goal', 'N/A')
            options = result.get('options', [])
            is_closing = result.get('is_closing', False)
            
            print(f"❓ Question: {question[:80]}{'...' if len(question) > 80 else ''}")
            print(f"🎯 Goal: {goal}")
            print(f"🔸 Options: {', '.join(options[:2])}{'...' if len(options) > 2 else ''}")
            print(f"🔚 Is Closing: {is_closing}")
            
            # Simulate customer answers based on goal
            simulated_answers = {
                "status_contact": "belum bayar",
                "payment_barrier": "belum ada uang", 
                "payment_timeline": "pas gajian tanggal 25",
                "payment_method": "transfer bank",
                "commitment_confirm": "ya pasti bayar",
                "follow_up_plan": "tolong diingatkan",
                "financial_capability": "ada kemampuan, cuma butuh waktu"
            }
            
            answer = simulated_answers.get(goal, "oke")
            print(f"💬 Customer Answer: {answer}")
            
            # Add to conversation history
            conversation.append({
                "q": question,
                "a": answer,
                "goal": goal
            })
            
            # Stop if conversation is closing
            if is_closing:
                print(f"✅ Conversation completed after {step} steps")
                break
                
        except Exception as e:
            print(f"❌ ERROR at step {step}: {e}")
            break
    
    print(f"\n📊 FINAL CONVERSATION SUMMARY:")
    print(f"📏 Total Questions: {len(conversation)}")
    print(f"🎯 Goals Covered: {[conv['goal'] for conv in conversation]}")
    
    # Analyze goal coverage
    goals_covered = set([conv['goal'] for conv in conversation])
    expected_goals = ["status_contact", "payment_barrier", "payment_timeline", "payment_method", "commitment_confirm", "follow_up_plan"]
    missing_goals = set(expected_goals) - goals_covered
    
    print(f"✅ Goals Achieved: {list(goals_covered)}")
    print(f"❌ Missing Goals: {list(missing_goals)}")
    
    coverage_percentage = (len(goals_covered) / len(expected_goals)) * 100
    print(f"📈 Goal Coverage: {coverage_percentage:.1f}%")
    
    return coverage_percentage >= 80  # 80% coverage required

def test_multi_mode_goal_coverage():
    """Test goal coverage untuk semua mode"""
    print(f"\n🎯 TESTING MULTI-MODE GOAL COVERAGE")
    print("=" * 60)
    
    modes = ["telecollection", "winback", "retention"]
    results = {}
    
    for mode in modes:
        print(f"\n📋 Testing {mode.upper()} mode")
        print("-" * 30)
        
        conversation = []
        goals_achieved = set()
        
        # Simulate 5 question conversation
        for step in range(1, 6):
            try:
                result = generate_question(mode, conversation)
                goal = result.get('goal', 'unknown')
                question = result.get('question', '')
                
                print(f"Step {step}: {goal} - {question[:50]}...")
                
                # Simulate positive answer
                answer = "ya, baik" if step % 2 == 0 else "setuju"
                conversation.append({
                    "q": question,
                    "a": answer, 
                    "goal": goal
                })
                
                goals_achieved.add(goal)
                
            except Exception as e:
                print(f"Error at step {step}: {e}")
                break
        
        results[mode] = {
            "goals_achieved": list(goals_achieved),
            "question_count": len(conversation)
        }
        
        print(f"✅ Goals: {list(goals_achieved)}")
        print(f"📏 Questions: {len(conversation)}")
    
    return results

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE END-TO-END TESTING")
    print("=" * 60)
    
    # Test 1: End-to-end telecollection
    telecollection_ok = test_end_to_end_conversation()
    
    # Test 2: Multi-mode goal coverage
    multi_mode_results = test_multi_mode_goal_coverage()
    
    print(f"\n{'='*60}")
    print("🏁 FINAL RESULTS")
    print(f"{'='*60}")
    print(f"✅ Telecollection E2E: {'PASS' if telecollection_ok else 'FAIL'}")
    
    for mode, result in multi_mode_results.items():
        goals_count = len(result['goals_achieved'])
        questions_count = result['question_count']
        print(f"✅ {mode.title()}: {goals_count} goals, {questions_count} questions")
    
    if telecollection_ok:
        print("🎉 END-TO-END CONVERSATION FLOW WORKING PERFECTLY!")
    else:
        print("⚠️  Some issues need attention")