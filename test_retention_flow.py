#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick test for Retention mode with new comprehensive knowledge base
"""
from backend.app.services.gpt_service import generate_question

def test_retention_flow():
    """Test basic retention conversation flow"""
    print("=" * 60)
    print("RETENTION MODE TEST - Comprehensive Knowledge Base")
    print("=" * 60)
    
    conv = []
    
    # Step 0: Greeting and identity verification
    print("\n[STEP 0] Greeting/Identity")
    conv.append({
        "question": "Selamat siang, perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Budi?",
        "answer": "Ya, benar"
    })
    q0 = generate_question('retention', conv)
    print(f"Next Goal: {q0.get('goal')}")
    print(f"Question: {q0.get('question')[:80]}...")
    
    # Step 1: Service check
    print("\n[STEP 1] Service Check")
    conv.append({
        "question": q0.get('question'),
            "goal": q0.get('goal'),
        "answer": "Iya layanan saya terputus"
    })
    q1 = generate_question('retention', conv)
    print(f"Next Goal: {q1.get('goal')}")
    print(f"Question: {q1.get('question')[:80]}...")
    
    # Step 2: Promo permission
    print("\n[STEP 2] Promo Permission")
    conv.append({
        "question": q1.get('question'),
            "goal": q1.get('goal'),
        "answer": "Boleh, silakan"
    })
    q2 = generate_question('retention', conv)
    print(f"Next Goal: {q2.get('goal')}")
    print(f"Question: {q2.get('question')[:80]}...")
    
    # Step 3: Promo detail
    print("\n[STEP 3] Promo Detail")
    conv.append({
        "question": q2.get('question'),
            "goal": q2.get('goal'),
        "answer": "Oke saya dengarkan"
    })
    q3 = generate_question('retention', conv)
    print(f"Next Goal: {q3.get('goal')}")
    print(f"Question: {q3.get('question')[:80]}...")
    
    # Step 4: Activation interest
    print("\n[STEP 4] Activation Interest")
    conv.append({
        "question": q3.get('question'),
            "goal": q3.get('goal'),
        "answer": "Berminat sih"
    })
    q4 = generate_question('retention', conv)
    print(f"Next Goal: {q4.get('goal')}")
    print(f"Question: {q4.get('question')[:80]}...")
    
    # Step 5: Payment confirmation
    print("\n[STEP 5] Payment Confirmation")
    conv.append({
        "question": q4.get('question'),
            "goal": q4.get('goal'),
        "answer": "Oke lanjut"
    })
    q5 = generate_question('retention', conv)
    print(f"Next Goal: {q5.get('goal')}")
    print(f"Question: {q5.get('question')[:80]}...")
    
    # Step 6: Payment timing
    print("\n[STEP 6] Payment Timing")
    conv.append({
        "question": q5.get('question'),
            "goal": q5.get('goal'),
        "answer": "Besok"
    })
    q6 = generate_question('retention', conv)
    print(f"Next Goal: {q6.get('goal')}")
    print(f"Question: {q6.get('question')[:80]}...")
    print(f"Is Closing: {q6.get('is_closing', False)}")
    
    print("\n" + "=" * 60)
    print("✅ RETENTION FLOW TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_retention_flow()
