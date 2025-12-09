#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test generate_question function
"""

import sys
import os
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

try:
    from backend.app.services.gpt_service import generate_question, TELECOLLECTION_QUESTIONS
    
    print("✅ Import berhasil")
    print(f"✅ TELECOLLECTION_QUESTIONS keys: {list(TELECOLLECTION_QUESTIONS.keys())}")
    
    # Test generate question
    conversation_history = [
        {
            "question": "Halo, bagaimana kabar Anda hari ini?",
            "answer": "Baik pak, terima kasih",
            "goal": "status_contact"
        }
    ]
    
    print("\nTesting generate_question...")
    result = generate_question("telecollection", conversation_history)
    
    print(f"✅ Result: {result}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()