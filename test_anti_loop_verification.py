#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Anti-Loop System - Verify no questions repeat
Tests Branch A (Sudah berhenti) progression with duplicate detection
"""
import requests
import json
from datetime import datetime
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

API_URL = "http://localhost:8000/api/v1/endpoints/conversation"

def test_anti_loop_branch_a():
    """Test Branch A with anti-loop system active"""
    print("=" * 80)
    print("TEST: Anti-Loop System - Branch A (Sudah berhenti)")
    print("=" * 80)
    
    # Start new conversation
    conversation_history = []
    
    start_response = requests.post(
        f"{API_URL}/cs-chatbot/start",
        json={
            "mode": "winback",
            "conversation_history": conversation_history,
            "customer_id": "TEST_ANTILOOP_001"
        }
    )
    
    if start_response.status_code != 200:
        print(f"❌ Failed to start conversation: {start_response.status_code}")
        print(f"Response: {start_response.text}")
        return
    
    start_data = start_response.json()
    first_question = start_data.get('question', {}).get('question', 'N/A')
    first_goal = start_data.get('question', {}).get('goal', 'unknown')
    
    print(f"\n✅ Conversation started")
    print(f"Q1 ({first_goal}): {first_question}")
    
    # Track all questions to detect duplicates
    all_questions = [first_question]
    
    # Define test flow
    test_flow = [
        ("Ya, benar", "greeting_identity → service_status"),
        ("Sudah berhenti", "service_status (Branch A) → reason_inquiry"),
        ("Pindah rumah", "reason_inquiry → device_check"),
        ("Masih ada", "device_check → current_provider"),
        ("Sekarang pakai IndiHome", "current_provider → stop_confirmation"),
        ("Ya, tetap mau berhenti", "stop_confirmation → closing_thanks")
    ]
    
    duplicate_detected = False
    
    for step_num, (user_answer, expected_flow) in enumerate(test_flow, 2):
        print(f"\n{'=' * 80}")
        print(f"STEP {step_num}: {expected_flow}")
        print(f"{'=' * 80}")
        print(f"User: {user_answer}")
        
        # Update conversation history with answer
        conversation_history.append({
            "question": all_questions[-1],
            "answer": user_answer,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate next question
        answer_response = requests.post(
            f"{API_URL}/cs-chatbot/start",
            json={
                "mode": "winback",
                "conversation_history": conversation_history,
                "customer_id": "TEST_ANTILOOP_001"
            }
        )
        
        if answer_response.status_code != 200:
            print(f"❌ Failed at step {step_num}: {answer_response.status_code}")
            print(f"Response: {answer_response.text}")
            break
        
        answer_data = answer_response.json()
        
        # Extract question and goal
        next_question = answer_data.get("question", {}).get("question", "N/A")
        next_goal = answer_data.get("question", {}).get("goal", "unknown")
        goal_status = answer_data.get("goal_status", {})
        
        print(f"\n📊 Status:")
        print(f"  Next Goal: {next_goal}")
        print(f"  Goals Completed: {goal_status.get('completed', 0)}/{goal_status.get('total', 0)}")
        print(f"  Conversation Complete: {goal_status.get('all_completed', False)}")
        
        print(f"\nQ{step_num} ({next_goal}): {next_question}")
        
        # Check for duplicates
        if next_question in all_questions:
            print(f"\n⚠️ DUPLICATE DETECTED! Question already asked before:")
            print(f"   Question: {next_question}")
            print(f"   Previous occurrence: Step {all_questions.index(next_question) + 1}")
            duplicate_detected = True
        
        all_questions.append(next_question)
        
        # Check if conversation ended
        if goal_status.get('all_completed'):
            print(f"\n✅ Conversation completed at step {step_num}")
            break
        
        # Add small pause
        import time
        time.sleep(0.5)
    
    print(f"\n{'=' * 80}")
    print("FINAL VERIFICATION")
    print(f"{'=' * 80}")
    print(f"Total Questions Asked: {len(all_questions)}")
    print(f"Unique Questions: {len(set(all_questions))}")
    
    if duplicate_detected:
        print("\n❌ ANTI-LOOP FAILED: Duplicates were detected")
        print("\nAll questions in order:")
        for i, q in enumerate(all_questions, 1):
            print(f"  {i}. {q}")
    else:
        print("\n✅ ANTI-LOOP SUCCESS: No duplicate questions detected")
        print("All questions were unique - system progressed cleanly through Branch A")
    
    return not duplicate_detected

if __name__ == "__main__":
    try:
        success = test_anti_loop_branch_a()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
