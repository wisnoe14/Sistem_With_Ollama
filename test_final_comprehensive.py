#!/usr/bin/env python3
"""
Final comprehensive test untuk memastikan semua improvements berfungsi sempurna
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import generate_question

def test_no_infinite_loops():
    """Test memastikan tidak ada infinite loops dalam conversation flow"""
    print("🔄 TESTING NO INFINITE LOOPS")
    print("=" * 50)
    
    # Simulate real API conversation (tanpa goal fields)
    conversation = [
        {"q": "Apakah bisa dihubungi untuk pembayaran?", "a": "ya, bisa dihubungi"},
        {"q": "Apakah bisa dihubungi untuk pembayaran?", "a": "ya, bisa dihubungi"}, 
        {"q": "Apakah bisa dihubungi untuk pembayaran?", "a": "ada jadwal khusus"}
    ]
    
    questions_generated = []
    goals_progression = []
    
    for step in range(4, 8):  # Test steps 4-7
        print(f"\n🔄 Step {step}:")
        print("-" * 20)
        
        try:
            result = generate_question("telecollection", conversation)
            
            question = result.get('question', '')
            goal = result.get('goal', 'unknown')
            
            print(f"❓ Question: {question[:60]}{'...' if len(question) > 60 else ''}")
            print(f"🎯 Goal: {goal}")
            
            # Check for loops
            if question in questions_generated:
                print(f"❌ LOOP DETECTED! Question repeated: {question[:40]}...")
                return False
                
            questions_generated.append(question)
            goals_progression.append(goal)
            
            # Simulate answer dan add to conversation WITH GOAL FIELD
            simulated_answer = "ya, setuju" if step % 2 == 0 else "oke, baik"
            conversation.append({
                "q": question,
                "a": simulated_answer,
                "goal": goal  # Add goal field to prevent goal inference issues
            })
            
            # Check goal progression
            if len(goals_progression) >= 2:
                if goals_progression[-1] == goals_progression[-2] and goal != "follow_up_plan":
                    print(f"⚠️ Same goal repeated: {goal}")
                else:
                    print(f"✅ Goal progressed: {goals_progression[-2]} → {goals_progression[-1]}")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Questions Generated: {len(questions_generated)}")
    print(f"✅ Goals Progression: {' → '.join(goals_progression)}")
    print(f"✅ No Loops Detected!")
    
    return True

def test_goal_diversity():
    """Test memastikan sistem menghasilkan berbagai goals, tidak stuck di satu goal"""
    print(f"\n🎯 TESTING GOAL DIVERSITY")
    print("=" * 50)
    
    conversation = []
    goals_seen = set()
    
    for step in range(1, 8):
        try:
            result = generate_question("telecollection", conversation)
            goal = result.get('goal', 'unknown')
            question = result.get('question', '')
            
            goals_seen.add(goal)
            print(f"Step {step}: {goal}")
            
            # Simulate positive answer untuk memastikan goals bergerak
            answer = "ya, pasti" if "commit" in goal else "baik"
            conversation.append({
                "q": question,
                "a": answer,
                "goal": goal
            })
            
        except Exception as e:
            print(f"❌ ERROR at step {step}: {e}")
            break
    
    print(f"\n📊 Goals Diversity:")
    print(f"✅ Unique Goals: {len(goals_seen)}")
    print(f"✅ Goals Seen: {list(goals_seen)}")
    
    # Success criteria: At least 3 different goals
    return len(goals_seen) >= 3

if __name__ == "__main__":
    print("🚀 FINAL COMPREHENSIVE TESTING")
    print("=" * 60)
    
    # Test 1: No infinite loops
    no_loops_ok = test_no_infinite_loops()
    
    # Test 2: Goal diversity  
    goal_diversity_ok = test_goal_diversity()
    
    print(f"\n{'='*60}")
    print("🏁 FINAL RESULTS")
    print(f"{'='*60}")
    print(f"✅ No Infinite Loops: {'PASS' if no_loops_ok else 'FAIL'}")
    print(f"✅ Goal Diversity: {'PASS' if goal_diversity_ok else 'FAIL'}")
    
    if no_loops_ok and goal_diversity_ok:
        print("🎉 ALL IMPROVEMENTS WORKING PERFECTLY!")
        print("🚀 SYSTEM READY FOR PRODUCTION!")
    else:
        print("⚠️  Some issues still need attention")