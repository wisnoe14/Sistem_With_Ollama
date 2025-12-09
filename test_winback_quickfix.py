#!/usr/bin/env python3
"""
🎯 TEST WINBACK QUICK FIX
Test singkat untuk memastikan perbaikan sudah bekerja
"""

import sys
import os
sys.path.append('backend')

from app.services.gpt_service import (
    generate_question,
    check_winback_goals,
    determine_winback_next_goal,
    CS_DATASET
)

def test_first_question():
    """Test first question generation"""
    print("1️⃣ TESTING FIRST QUESTION:")
    conversation = []
    result = generate_question("winback", conversation)
    print(f"   ❓ Question: {result['question']}")
    print(f"   🔸 Options: {result['options']}")
    print(f"   🎯 Goal: {result['goal']}")
    return result

def test_goal_detection():
    """Test goal detection from conversation"""
    print("\n2️⃣ TESTING GOAL DETECTION:")
    
    # Simulate conversation with greeting
    conversation = [
        {
            "q": "Selamat pagi/siang/sore, Bapak/Ibu. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu [Nama Pelanggan]?",
            "a": "Ya, benar"
        }
    ]
    
    goals = check_winback_goals(conversation)
    print(f"   📊 Progress: {goals['achievement_percentage']:.1f}%")
    print(f"   ✅ Achieved: {goals['achieved_goals']}")
    print(f"   ❌ Missing: {goals['missing_goals']}")
    
    return goals

def test_next_goal():
    """Test next goal determination"""
    print("\n3️⃣ TESTING NEXT GOAL:")
    
    conversation = [
        {
            "q": "Selamat pagi/siang/sore, Bapak/Ibu. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu [Nama Pelanggan]?",
            "a": "Ya, benar"
        }
    ]
    
    goals = check_winback_goals(conversation)
    next_goal = determine_winback_next_goal(conversation, goals)
    print(f"   🎯 Next Goal: {next_goal}")
    
    return next_goal

def test_second_question():
    """Test second question generation"""
    print("\n4️⃣ TESTING SECOND QUESTION:")
    
    conversation = [
        {
            "q": "Selamat pagi/siang/sore, Bapak/Ibu. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu [Nama Pelanggan]?",
            "a": "Ya, benar"
        }
    ]
    
    result = generate_question("winback", conversation)
    print(f"   ❓ Question: {result['question'][:80]}...")
    print(f"   🔸 Options: {result['options']}")
    print(f"   🎯 Goal: {result['goal']}")
    
    return result

def main():
    print("🚀 WINBACK QUICK FIX TEST")
    print("=" * 50)
    
    try:
        # Test CS_DATASET update
        print("📋 CS_DATASET Winback:")
        if "winback" in CS_DATASET and CS_DATASET["winback"]:
            first_question = CS_DATASET["winback"][0]
            print(f"   ✅ Updated: {first_question['question'][:50]}...")
        else:
            print("   ❌ Not found")
            
        test_first_question()
        test_goal_detection()
        test_next_goal()
        test_second_question()
        
        print("\n" + "=" * 50)
        print("🎉 QUICK TEST COMPLETED!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()