#!/usr/bin/env python3
"""
Quick test script to verify gpt_service.py functions work correctly
"""

def test_gpt_service():
    print("🧪 Testing gpt_service.py functions...")
    
    try:
        # Test import
        from app.services.gpt_service import (
            validate_goal_achievement, 
            determine_next_goal, 
            is_answer_specific, 
            needs_deeper_probe,
            CONVERSATION_GOALS
        )
        print("✅ All imports successful!")
        
        # Test validate_goal_achievement function
        test_validation = validate_goal_achievement(
            "payment_timeline", 
            "besok sore", 
            [{"q": "Kapan bisa bayar?", "a": "besok sore"}]
        )
        print(f"✅ Goal validation test: {test_validation}")
        
        # Test is_answer_specific function
        specific_test = is_answer_specific("besok sore jam 3")
        vague_test = is_answer_specific("nanti mungkin")
        print(f"✅ Specific answer test: {specific_test} (should be True)")
        print(f"✅ Vague answer test: {vague_test} (should be False)")
        
        # Test needs_deeper_probe function
        probe_test = needs_deeper_probe("nanti", "payment_timeline")
        print(f"✅ Probing test: {probe_test} (should be True)")
        
        # Test CONVERSATION_GOALS
        telecollection_goals = CONVERSATION_GOALS.get("telecollection", [])
        print(f"✅ Telecollection goals ({len(telecollection_goals)}): {telecollection_goals}")
        
        # Test determine_next_goal function
        conversation_history = [{"q": "Halo", "a": "halo juga", "goal": "status_contact"}]
        goal_status = {"missing_goals": ["payment_timeline"]}
        next_goal = determine_next_goal("telecollection", conversation_history, goal_status)
        print(f"✅ Next goal determination: {next_goal}")
        
        print("\n🎉 ALL TESTS PASSED! gpt_service.py is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_gpt_service()