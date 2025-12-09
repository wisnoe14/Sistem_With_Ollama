#!/usr/bin/env python3
"""
Test Manual Answer Integration dengan Goal Tracking System
Menguji apakah jawaban manual sudah terintegrasi dengan sistem goal tracking
"""

import requests
import json
import pprint

def test_manual_answer_integration():
    BASE_URL = "http://localhost:8000"
    CUSTOMER_ID = "ICON12345_MANUAL_TEST"
    
    print("🧪 Testing Manual Answer Integration dengan Goal Tracking")
    print("="*60)
    
    # Test 1: Process manual answer with conversation history
    print("\n📝 Test 1: Manual Answer Processing")
    
    # Simulasi conversation history
    conversation_history = [
        {
            "q": "Halo, untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?",
            "a": "belum bayar"
        }
    ]
    
    # Test manual answer
    manual_answer_payload = {
        "customer_id": CUSTOMER_ID,
        "topic": "telecollection",
        "conversation": conversation_history,
        "current_question": "Apakah ada kendala khusus yang membuat pembayaran belum bisa dilakukan?",
        "customer_answer": "ada masalah keuangan keluarga yang mendadak",
        "input_type": "manual"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/endpoints/conversation/process-answer",
            json=manual_answer_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Manual Answer Processing - Status: {response.status_code}")
            print(f"📄 Response Keys: {list(data.keys())}")
            
            # Check goal tracking information
            if "goal_progress" in data:
                goal_progress = data["goal_progress"]
                print(f"🎯 Goals Completed: {goal_progress['completed_goals']}")
                print(f"📋 Remaining Goals: {goal_progress['remaining_goals']}")
                print(f"📊 Completion: {goal_progress['completion_percentage']:.1f}%")
            
            if "question" in data:
                print(f"❓ Next Question: {data['question'][:100]}...")
            
            print(f"🔄 Conversation Length: {data.get('conversation_length', 'N/A')}")
            print(f"📝 Input Type: {data.get('input_type', 'N/A')}")
            
        else:
            print(f"❌ Manual Answer Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Manual Answer Exception: {str(e)}")
    
    # Test 2: Selected option processing
    print(f"\n📝 Test 2: Selected Option Processing")
    
    selected_option_payload = {
        "customer_id": CUSTOMER_ID,
        "topic": "telecollection", 
        "conversation": conversation_history,
        "current_question": "Kapan kira-kira bisa melakukan pembayaran?",
        "customer_answer": "Minggu depan setelah gajian turun",
        "input_type": "selected"
    }
    
    try:
        response2 = requests.post(
            f"{BASE_URL}/api/v1/endpoints/conversation/process-answer",
            json=selected_option_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ Selected Option Processing - Status: {response2.status_code}")
            
            if "goal_progress" in data2:
                goal_progress2 = data2["goal_progress"]
                print(f"🎯 Goals Completed: {goal_progress2['completed_goals']}")
                print(f"📋 Remaining Goals: {goal_progress2['remaining_goals']}")
                print(f"📊 Completion: {goal_progress2['completion_percentage']:.1f}%")
                
        else:
            print(f"❌ Selected Option Error: {response2.status_code}")
            print(f"📄 Response: {response2.text}")
            
    except Exception as e:
        print(f"💥 Selected Option Exception: {str(e)}")
    
    # Test 3: Compare dengan generate-simulation-questions
    print(f"\n📝 Test 3: Comparison dengan Generate Simulation Questions")
    
    simulation_payload = {
        "customer_id": CUSTOMER_ID,
        "topic": "telecollection",
        "conversation": conversation_history,
        "user": "test@iconnet.co.id"
    }
    
    try:
        response3 = requests.post(
            f"{BASE_URL}/api/v1/endpoints/conversation/generate-simulation-questions",
            json=simulation_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response3.status_code == 200:
            data3 = response3.json()
            print(f"✅ Simulation Questions - Status: {response3.status_code}")
            print(f"❓ Question: {data3.get('question', 'N/A')[:100]}...")
            print(f"📋 Options: {len(data3.get('options', []))} options available")
            
        else:
            print(f"❌ Simulation Error: {response3.status_code}")
            
    except Exception as e:
        print(f"💥 Simulation Exception: {str(e)}")
    
    print(f"\n{'='*60}")
    print("🏆 Manual Answer Integration Test Completed!")

if __name__ == "__main__":
    test_manual_answer_integration()