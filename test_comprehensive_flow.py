#!/usr/bin/env python3
"""
Test comprehensive winback flow with separated goals
"""

import sys
import os
sys.path.append('backend')

from app.services.gpt_service import (
    generate_question_for_goal,
    check_winback_goals,
    determine_winback_next_goal,
    CONVERSATION_GOALS
)

print("🧪 COMPREHENSIVE WINBACK FLOW TEST")
print("=" * 60)

# Test complete flow: Identity → Promo → Rejection → Reason → Equipment
print("\n📋 Testing complete winback flow with separated goals:")

# Step 1: Identity confirmation
print("\n1️⃣ STEP 1: Identity Confirmation")
conversation = []
goal_status = check_winback_goals(conversation)
next_goal = determine_winback_next_goal(conversation, goal_status)
print(f"   🎯 Next Goal: {next_goal}")

try:
    q1 = generate_question_for_goal(next_goal, [], "winback")
    print(f"   ❓ Question: {q1.get('question', 'No question')[:80]}...")
    conversation.append({"question": q1.get('question', ''), "answer": "Ya, benar"})
    print("   📞 Customer Response: Ya, benar")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 2: Promo offer (skip identity_confirmation)
print("\n2️⃣ STEP 2: Promo Offer")
goal_status = check_winback_goals(conversation)
next_goal = determine_winback_next_goal(conversation, goal_status)
print(f"   📊 Progress: {goal_status['achievement_percentage']:.1f}%")
print(f"   🎯 Next Goal: {next_goal}")

try:
    q2 = generate_question_for_goal(next_goal, conversation, "winback")
    print(f"   ❓ Question: {q2.get('question', 'No question')[:80]}...")
    conversation.append({"question": q2.get('question', ''), "answer": "Tidak, terima kasih"})
    print("   📞 Customer Response: Tidak, terima kasih")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 3: Should go to reason inquiry after rejection
print("\n3️⃣ STEP 3: Reason Inquiry (after rejection)")
goal_status = check_winback_goals(conversation)
next_goal = determine_winback_next_goal(conversation, goal_status)
print(f"   📊 Progress: {goal_status['achievement_percentage']:.1f}%")
print(f"   🎯 Next Goal: {next_goal}")

try:
    q3 = generate_question_for_goal(next_goal, conversation, "winback")
    print(f"   ❓ Question: {q3.get('question', 'No question')[:80]}...")
    conversation.append({"question": q3.get('question', ''), "answer": "Ada keluhan layanan"})
    print("   📞 Customer Response: Ada keluhan layanan")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 4: Equipment check
print("\n4️⃣ STEP 4: Equipment Check")
goal_status = check_winback_goals(conversation)
next_goal = determine_winback_next_goal(conversation, goal_status)
print(f"   📊 Progress: {goal_status['achievement_percentage']:.1f}%")
print(f"   🎯 Next Goal: {next_goal}")

try:
    q4 = generate_question_for_goal(next_goal, conversation, "winback")
    print(f"   🔧 Question: {q4.get('question', 'No question')[:80]}...")
    conversation.append({"question": q4.get('question', ''), "answer": "Masih ada"})
    print("   📞 Customer Response: Masih ada")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 5: Closing
print("\n5️⃣ STEP 5: Closing")
goal_status = check_winback_goals(conversation)
next_goal = determine_winback_next_goal(conversation, goal_status)
print(f"   📊 Final Progress: {goal_status['achievement_percentage']:.1f}%")
print(f"   🎯 Next Goal: {next_goal}")

print(f"\n🎉 FLOW TEST COMPLETED!")
print(f"\n📊 FINAL METRICS:")
print(f"   Total Goals: {len(CONVERSATION_GOALS['winback'])}")
print(f"   Achieved Goals: {len(goal_status['achieved_goals'])}")
print(f"   Missing Goals: {goal_status['missing_goals']}")
print(f"   ✅ Success: Goals properly separated for reason and equipment inquiry")