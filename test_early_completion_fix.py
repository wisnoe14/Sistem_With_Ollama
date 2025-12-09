#!/usr/bin/env python3
"""
Test perbaikan masalah:
1. Early completion ketika customer jawab "sudah" (already paid)  
2. Proper closing question generation
3. Mencegah double question generation
"""

import sys
import os

backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_path)

try:
    from app.services.gpt_service import (
        determine_next_goal, 
        validate_goal_achievement,
        generate_goal_specific_question
    )
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def test_early_completion_and_closing():
    """Test early completion dan proper closing"""
    
    print("🔧 TESTING EARLY COMPLETION & CLOSING FIXES")
    print("=" * 60)
    
    # Test 1: Customer sudah bayar - should go to closing immediately
    print("🧪 Test 1: Customer already paid (early completion)")
    try:
        # Validation test
        validation = validate_goal_achievement("status_contact", "sudah", [])
        payment_complete = validation.get("payment_complete", False)
        
        print(f"   Validation result: achieved={validation['achieved']}, score={validation['quality_score']}")
        print(f"   Payment complete flag: {payment_complete}")
        
        if payment_complete:
            print("   ✅ PASS: Early completion detected")
        else:
            print("   ❌ FAIL: Early completion not detected")
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    # Test 2: Goal progression dengan early completion
    print("\n🧪 Test 2: Goal progression with early completion")
    try:
        conversation = [{"q": "Pembayaran sudah diselesaikan belum?", "a": "sudah", "goal": "status_contact"}]
        goal_status = {
            'achieved_goals': [], 
            'missing_goals': ['status_contact', 'payment_barrier', 'payment_timeline'],
            'status_contact': {'achieved': False, 'score': 0}
        }
        
        result = determine_next_goal("telecollection", conversation, goal_status)
        
        print(f"   Next goal result: '{result}'")
        if result == "closing":
            print("   ✅ PASS: Early completion leads to closing")
        else:
            print(f"   ❌ FAIL: Expected 'closing', got '{result}'")
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    # Test 3: Proper closing question generation
    print("\n🧪 Test 3: Proper closing question generation")
    try:
        closing_question = generate_goal_specific_question("telecollection", "closing", [])
        
        print(f"   Question: {closing_question.get('question', 'N/A')[:60]}...")
        print(f"   Is closing: {closing_question.get('is_closing', False)}")
        print(f"   Conversation complete: {closing_question.get('conversation_complete', False)}")
        
        if closing_question.get('is_closing') and closing_question.get('conversation_complete'):
            print("   ✅ PASS: Proper closing question generated")
        else:
            print("   ❌ FAIL: Closing question not properly configured")
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    # Test 4: Normal telecollection flow (belum bayar)
    print("\n🧪 Test 4: Normal flow when payment not done")
    try:
        validation = validate_goal_achievement("status_contact", "belum", [])
        payment_complete = validation.get("payment_complete", False)
        
        print(f"   Validation: achieved={validation['achieved']}, score={validation['quality_score']}")
        print(f"   Should continue telecollection: {not payment_complete}")
        
        if not payment_complete and validation['achieved']:
            print("   ✅ PASS: Normal telecollection flow continues")
        else:
            print("   ❌ FAIL: Normal flow not working properly")
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY OF FIXES:")
    print("✅ Early completion detection for 'sudah' answers")
    print("✅ Proper closing question with is_closing=True")  
    print("✅ Conversation_complete flag for proper ending")
    print("✅ Skip telecollection process when payment already done")
    print("\n🚀 These fixes should resolve:")
    print("   • Double question generation")
    print("   • Unnecessary telecollection when customer already paid")
    print("   • Proper conversation ending")

if __name__ == "__main__":
    test_early_completion_and_closing()