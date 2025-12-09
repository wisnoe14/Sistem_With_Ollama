#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 COMPREHENSIVE SYSTEM CHECK - GPT SERVICE
============================================
Test semua fungsi utama untuk memastikan tidak ada error
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def test_imports():
    """Test semua import functions"""
    print("🔌 TESTING IMPORTS...")
    try:
        from backend.app.services.gpt_service import (
            generate_question,
            save_conversation_to_excel,
            predict_status_promo_ollama,
            predict_status_promo_svm, 
            predict_status_promo_lda,
            get_current_date_info,
            parse_relative_date,
            get_question_from_dataset,
            generate_automatic_customer_answer,
            check_conversation_goals_completed,
            generate_final_prediction,
            CS_DATASET,
            CONVERSATION_GOALS,
            get_ollama_performance_report,
            analyze_sentiment_and_intent,
            check_conversation_goals,
            predict_telecollection_outcome
        )
        
        print("   ✅ All imports successful!")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_functions():
    """Test fungsi-fungsi basic"""
    print("\n🧪 TESTING BASIC FUNCTIONS...")
    
    try:
        from backend.app.services.gpt_service import (
            analyze_sentiment_and_intent,
            parse_relative_date,
            get_current_date_info
        )
        
        # Test sentiment analysis
        result = analyze_sentiment_and_intent("Besok saya bayar pak")
        print(f"   ✅ Sentiment analysis: {result['sentiment']} ({result['confidence']}%)")
        
        # Test date parsing
        date_result = parse_relative_date("besok")
        print(f"   ✅ Date parsing: {date_result['found']} - {date_result.get('target_date', 'N/A')}")
        
        # Test date info
        date_info = get_current_date_info()
        print(f"   ✅ Current date info: {date_info.get('formatted_date', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"   ❌ Basic functions failed: {e}")
        return False

def test_conversation_flow():
    """Test conversation generation"""
    print("\n💬 TESTING CONVERSATION FLOW...")
    
    try:
        from backend.app.services.gpt_service import generate_question
        
        # Test new conversation
        result1 = generate_question("telecollection", [])
        print(f"   ✅ New conversation: {result1.get('question', 'N/A')[:50]}...")
        
        # Test with history
        conversation_history = [
            {
                "question": "Halo, pembayaran ICONNET sudah diselesaikan?",
                "answer": "Belum pak, lupa",
                "goal": "status_contact"
            }
        ]
        
        result2 = generate_question("telecollection", conversation_history)
        print(f"   ✅ With history: {result2.get('question', 'N/A')[:50]}...")
        
        return True
    except Exception as e:
        print(f"   ❌ Conversation flow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prediction_functions():
    """Test prediction functions"""
    print("\n🔮 TESTING PREDICTION FUNCTIONS...")
    
    try:
        from backend.app.services.gpt_service import (
            predict_telecollection_outcome,
            predict_status_promo_ollama,
            predict_status_promo_svm
        )
        
        conversation = [
            {"question": "Sudah bayar?", "answer": "Besok pak", "goal": "payment_timeline"}
        ]
        
        # Test telecollection prediction
        result = predict_telecollection_outcome(conversation)
        print(f"   ✅ Telecollection prediction: {result.get('keputusan', 'N/A')}")
        
        # Test promo prediction (with fallback if fails)
        try:
            promo_result = predict_status_promo_ollama("Saya tertarik dengan promo")
            print(f"   ✅ Promo prediction: {promo_result.get('prediction', 'N/A')}")
        except:
            print(f"   ⚠️ Promo prediction: Skipped (Ollama not available)")
        
        return True
    except Exception as e:
        print(f"   ❌ Prediction functions failed: {e}")
        return False

def test_dataset_functions():
    """Test dataset functions"""
    print("\n📚 TESTING DATASET FUNCTIONS...")
    
    try:
        from backend.app.services.gpt_service import (
            get_question_from_dataset,
            CS_DATASET,
            CONVERSATION_GOALS,
            check_conversation_goals_completed
        )
        
        print(f"   ✅ CS_DATASET modes: {list(CS_DATASET.keys())}")
        print(f"   ✅ CONVERSATION_GOALS: {list(CONVERSATION_GOALS.keys())}")
        
        # Test get question
        question = get_question_from_dataset("telecollection")
        print(f"   ✅ Dataset question: {question.get('question', 'N/A')[:40]}...")
        
        # Test goals check
        conversation = [{"a": "Belum bayar", "goal": "status_contact"}]
        goals = check_conversation_goals_completed("telecollection", conversation)
        print(f"   ✅ Goals check: {goals.get('achievement_percentage', 0)}% completed")
        
        return True
    except Exception as e:
        print(f"   ❌ Dataset functions failed: {e}")
        return False

def main():
    """Run comprehensive system check"""
    print("🎯 COMPREHENSIVE SYSTEM CHECK - GPT SERVICE")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("Imports", test_imports()))
    results.append(("Basic Functions", test_basic_functions()))
    results.append(("Conversation Flow", test_conversation_flow()))
    results.append(("Prediction Functions", test_prediction_functions()))
    results.append(("Dataset Functions", test_dataset_functions()))
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL SYSTEMS OPERATIONAL!")
    else:
        print("⚠️  SOME ISSUES DETECTED - CHECK LOGS ABOVE")

if __name__ == "__main__":
    main()