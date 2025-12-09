#!/usr/bin/env python3
"""
🎯 SIMPLE TEST untuk memastikan sistem berfungsi setelah cleanup
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def simple_test():
    print("🎯 SIMPLE SYSTEM TEST")
    print("=" * 40)
    
    try:
        # Test import sederhana
        from app.services.gpt_service import generate_question
        print("✅ Import gpt_service: SUCCESS")
        
        # Test simple conversation
        conversation = [
            {"question": "Test", "answer": "besok", "goal": "payment_timeline"}
        ]
        
        result = generate_question("telecollection", conversation)
        print(f"✅ Generate question: SUCCESS")
        print(f"   Is Closing: {result.get('is_closing', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = simple_test()
    if success:
        print("\n🚀 BASIC SYSTEM: WORKING")
    else:
        print("\n⚠️ SYSTEM: NEEDS FIX")