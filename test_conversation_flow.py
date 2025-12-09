#!/usr/bin/env python3
"""
Test script untuk memverifikasi perbaikan conversation flow - konteks dan continuity
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1/endpoints"
TEST_CUSTOMER_ID = "ICON12345"

def print_separator(title=""):
    print("\n" + "="*80)
    if title:
        print(f" {title} ")
        print("="*80)
    print()

def test_conversation_flow(mode="telecollection"):
    """Test natural conversation flow dengan contextual responses"""
    print_separator(f"Testing {mode.upper()} Conversation Flow with Context")
    
    conversation = []
    question_count = 0
    
    # Test scenario: Customer dengan masalah keuangan → timeline → commitment
    test_responses = [
        "Saya ada masalah keuangan saat ini pak, belum ada uang untuk bayar",
        "Kira-kira 5 hari lagi setelah gajian",
        "Ya saya yakin bisa tepat waktu, sudah saya catat di agenda"
    ]
    
    while question_count < len(test_responses):
        try:
            # Generate pertanyaan
            print(f"🔄 Generating question #{question_count + 1}...")
            
            response = requests.post(
                f"{API_BASE_URL}/conversation/generate-simulation-questions",
                json={
                    "customer_id": TEST_CUSTOMER_ID,
                    "topic": mode,
                    "conversation": conversation,
                    "user": "test@iconnet.co.id"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                question = data.get("question", "")
                options = data.get("options", [])
                
                print(f"📞 CS Agent: {question}")
                print(f"📋 Options: {options}")
                
                # Simulate customer response
                customer_answer = test_responses[question_count]
                print(f"👤 Customer: {customer_answer}")
                
                # Add to conversation
                conversation.append({
                    "q": question,
                    "a": customer_answer
                })
                
                # Verify contextual connection
                print("\n🔍 Context Analysis:")
                if question_count > 0:
                    previous_answer = conversation[-2]["a"].lower()
                    current_question = question.lower()
                    
                    # Check if question references previous answer
                    contextual_keywords = extract_keywords_from_answer(previous_answer)
                    question_contains_context = any(keyword in current_question for keyword in contextual_keywords)
                    
                    # Check for natural transitions
                    natural_transitions = [
                        "saya memahami", "baik", "oh begitu", "kalau begitu",
                        "berarti", "jadi", "untuk memastikan"
                    ]
                    has_natural_transition = any(transition in current_question for transition in natural_transitions)
                    
                    print(f"   • Keywords from previous answer: {contextual_keywords}")
                    print(f"   • Question contains context: {'✅' if question_contains_context else '❌'}")
                    print(f"   • Has natural transition: {'✅' if has_natural_transition else '❌'}")
                    
                    if question_contains_context or has_natural_transition:
                        print("   ✅ GOOD: Question naturally connects to previous answer")
                    else:
                        print("   ❌ ISSUE: Question doesn't connect to previous context")
                
                question_count += 1
                time.sleep(1)  # Brief pause
                
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                break
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            break
    
    print_separator("Conversation Summary")
    print("📝 Full Conversation Flow:")
    for i, exchange in enumerate(conversation, 1):
        print(f"\n{i}. CS: {exchange['q']}")
        print(f"   Customer: {exchange['a']}")
    
    # Test continuity score
    continuity_score = calculate_continuity_score(conversation)
    print(f"\n📊 Conversation Continuity Score: {continuity_score:.1f}/10")
    
    return conversation

def extract_keywords_from_answer(answer):
    """Extract key contextual words from customer answer"""
    keywords = []
    answer_lower = answer.lower()
    
    # Financial keywords
    if any(word in answer_lower for word in ["masalah", "kesulitan", "keuangan", "uang"]):
        keywords.extend(["masalah", "keuangan", "situasi"])
    
    # Time keywords
    if any(word in answer_lower for word in ["hari", "minggu", "gajian", "bulan"]):
        keywords.extend(["hari", "waktu", "gajian"])
    
    # Commitment keywords
    if any(word in answer_lower for word in ["yakin", "pasti", "agenda", "catat"]):
        keywords.extend(["yakin", "pasti", "komitmen"])
    
    return keywords

def calculate_continuity_score(conversation):
    """Calculate how well questions connect to previous answers"""
    if len(conversation) < 2:
        return 10.0
    
    total_score = 0
    scored_exchanges = 0
    
    for i in range(1, len(conversation)):
        previous_answer = conversation[i-1]["a"].lower()
        current_question = conversation[i]["q"].lower()
        
        score = 0
        
        # Check for keyword continuity
        keywords = extract_keywords_from_answer(previous_answer)
        if any(keyword in current_question for keyword in keywords):
            score += 4
        
        # Check for natural transitions
        transitions = ["saya memahami", "baik", "berarti", "jadi", "untuk memastikan"]
        if any(transition in current_question for transition in transitions):
            score += 3
        
        # Check for response acknowledgment
        if any(word in current_question for word in ["situasi", "kondisi", "rencana"]):
            score += 2
        
        # Check if question builds on previous answer
        if "kira-kira" in previous_answer and "kapan" in current_question:
            score += 1
        
        total_score += min(score, 10)
        scored_exchanges += 1
    
    return total_score / scored_exchanges if scored_exchanges > 0 else 10.0

def test_multiple_modes():
    """Test all conversation modes"""
    modes = ["telecollection", "winback", "retention"]
    
    for mode in modes:
        print_separator(f"Testing {mode.upper()} Mode")
        conversation = test_conversation_flow(mode)
        
        if conversation:
            print(f"✅ {mode} test completed with {len(conversation)} exchanges")
        else:
            print(f"❌ {mode} test failed")
        
        time.sleep(2)  # Pause between modes

if __name__ == "__main__":
    print_separator("CS ML Chatbot - Conversation Flow Context Test")
    print("🎯 Testing improved contextual conversation flow...")
    print("🔍 Checking if questions naturally connect to customer responses...")
    
    try:
        # Test telecollection mode in detail
        test_conversation_flow("telecollection")
        
        # Quick test of other modes
        print_separator("Quick Test - Other Modes")
        for mode in ["winback", "retention"]:
            print(f"\n🔄 Testing {mode}...")
            response = requests.post(
                f"{API_BASE_URL}/conversation/generate-simulation-questions",
                json={
                    "customer_id": TEST_CUSTOMER_ID,
                    "topic": mode,
                    "conversation": [],
                    "user": "test@iconnet.co.id"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {mode}: {data.get('question', '')[:60]}...")
            else:
                print(f"❌ {mode}: Failed")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print_separator("Test Complete")
    print("Check the console output above for contextual conversation analysis!")