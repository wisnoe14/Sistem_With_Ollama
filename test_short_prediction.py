#!/usr/bin/env python3
"""
Test Short Conversation Prediction Fix
Test apakah prediction logic sudah diperbaiki untuk conversation singkat dengan explicit closing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import predict_telecollection_status

def test_short_conversation_prediction():
    """Test prediction untuk conversation singkat dengan explicit closing"""
    print("=" * 60)
    print("📊 TESTING SHORT CONVERSATION PREDICTION FIX")
    print("=" * 60)
    
    # Test case 1: Customer says "belum" then "Selesai" (dari user report)
    test_answers_1 = ["belum", "Selesai"]
    test_conversation_1 = "belum selesai"
    
    print("\n📋 TEST 1: Customer says 'belum' then 'Selesai'")
    print(f"Answers: {test_answers_1}")
    
    result_1 = predict_telecollection_status(test_conversation_1, test_answers_1)
    
    print(f"\n📊 RESULT 1:")
    print(f"🎯 Prediction: {result_1.get('prediction', 'N/A')}")
    print(f"📈 Status: {result_1.get('status', 'N/A')}")
    print(f"🔍 Confidence: {result_1.get('confidence', 0):.3f}")
    print(f"💭 Alasan: {result_1.get('alasan', 'N/A')}")
    
    # Test case 2: Customer says "tidak bisa" then "cukup"
    test_answers_2 = ["tidak bisa", "cukup"]
    test_conversation_2 = "tidak bisa cukup"
    
    print(f"\n📋 TEST 2: Customer says 'tidak bisa' then 'cukup'")
    print(f"Answers: {test_answers_2}")
    
    result_2 = predict_telecollection_status(test_conversation_2, test_answers_2)
    
    print(f"\n📊 RESULT 2:")
    print(f"🎯 Prediction: {result_2.get('prediction', 'N/A')}")
    print(f"📈 Status: {result_2.get('status', 'N/A')}")
    print(f"🔍 Confidence: {result_2.get('confidence', 0):.3f}")
    print(f"💭 Alasan: {result_2.get('alasan', 'N/A')[:100]}...")
    
    # Test case 3: Customer says "akan bayar" then "selesai" (positive case)
    test_answers_3 = ["akan bayar", "selesai"]
    test_conversation_3 = "akan bayar selesai"
    
    print(f"\n📋 TEST 3: Customer says 'akan bayar' then 'selesai'")
    print(f"Answers: {test_answers_3}")
    
    result_3 = predict_telecollection_status(test_conversation_3, test_answers_3)
    
    print(f"\n📊 RESULT 3:")
    print(f"🎯 Prediction: {result_3.get('prediction', 'N/A')}")
    print(f"📈 Status: {result_3.get('status', 'N/A')}")
    print(f"🔍 Confidence: {result_3.get('confidence', 0):.3f}")
    print(f"💭 Alasan: {result_3.get('alasan', 'N/A')[:100]}...")
    
    # Test case 4: Normal longer conversation (should use original logic)
    test_answers_4 = ["belum", "susah", "tidak ada uang", "mungkin bulan depan", "pikir dulu"]
    test_conversation_4 = "belum susah tidak ada uang mungkin bulan depan pikir dulu"
    
    print(f"\n📋 TEST 4: Normal longer conversation (should use original logic)")
    print(f"Answers: {len(test_answers_4)} answers")
    
    result_4 = predict_telecollection_status(test_conversation_4, test_answers_4)
    
    print(f"\n📊 RESULT 4:")
    print(f"🎯 Prediction: {result_4.get('prediction', 'N/A')}")
    print(f"📈 Status: {result_4.get('status', 'N/A')}")
    print(f"🔍 Confidence: {result_4.get('confidence', 0):.3f}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY:")
    print(f"Test 1 (belum+selesai): {result_1.get('prediction')} - Confidence {result_1.get('confidence', 0):.3f}")
    print(f"Test 2 (tidak bisa+cukup): {result_2.get('prediction')} - Confidence {result_2.get('confidence', 0):.3f}")
    print(f"Test 3 (akan bayar+selesai): {result_3.get('prediction')} - Confidence {result_3.get('confidence', 0):.3f}")
    print(f"Test 4 (normal long): {result_4.get('prediction')} - Confidence {result_4.get('confidence', 0):.3f}")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_short_conversation_prediction()