"""
Quick API Test - Winback Mode
==============================
Test sederhana untuk memvalidasi winback mode via API endpoint.
"""

import requests
import json

API_URL = "http://localhost:8000/api/v1/conversation/generate-question"

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def test_winback_branch_a():
    """Test Branch A: Sudah berhenti"""
    print_header("TEST BRANCH A: SUDAH BERHENTI (via API)")
    
    # Step 1: greeting_identity
    response = requests.post(API_URL, json={
        "customer_name": "Ahmad",
        "agent_name": "Wisnu",
        "conversation_history": [],
        "mode": "winback"
    })
    data = response.json()
    print(f"Q1: {data['question'][:100]}...")
    print(f"Goal: {data['current_goal']}")
    assert data['current_goal'] == "greeting_identity"
    
    # Step 2: service_status
    response = requests.post(API_URL, json={
        "customer_name": "Ahmad",
        "agent_name": "Wisnu",
        "conversation_history": [
            {"q": data['question'], "a": "Ya, benar", "goal": "greeting_identity"}
        ],
        "mode": "winback"
    })
    data = response.json()
    print(f"\nQ2: {data['question'][:100]}...")
    print(f"Goal: {data['current_goal']}")
    assert data['current_goal'] == "service_status"
    
    # Step 3: reason_inquiry (after "Sudah berhenti")
    response = requests.post(API_URL, json={
        "customer_name": "Ahmad",
        "agent_name": "Wisnu",
        "conversation_history": [
            {"q": "greeting", "a": "Ya, benar", "goal": "greeting_identity"},
            {"q": data['question'], "a": "Sudah berhenti", "goal": "service_status"}
        ],
        "mode": "winback"
    })
    data = response.json()
    print(f"\nQ3: {data['question'][:100]}...")
    print(f"Goal: {data['current_goal']}")
    assert data['current_goal'] == "reason_inquiry"
    
    print("\n✅ BRANCH A TEST PASSED (API)")

def test_winback_branch_c():
    """Test Branch C: Tidak ada gangguan (unpaid)"""
    print_header("TEST BRANCH C: TIDAK ADA GANGGUAN (via API)")
    
    # Navigate to payment_status_info
    response = requests.post(API_URL, json={
        "customer_name": "Siti",
        "agent_name": "Wisnu",
        "conversation_history": [
            {"q": "greeting", "a": "Ya, benar", "goal": "greeting_identity"},
            {"q": "service status", "a": "Tidak ada gangguan", "goal": "service_status"}
        ],
        "mode": "winback"
    })
    data = response.json()
    print(f"Q: {data['question'][:150]}...")
    print(f"Goal: {data['current_goal']}")
    assert data['current_goal'] == "payment_status_info"
    
    # Check promo text
    assert "promo bayar 1 bulan gratis 1 bulan" in data['question'].lower()
    print("✅ Promo text validated: 'bayar 1 bulan gratis 1 bulan'")
    
    # Test tertarik path
    response = requests.post(API_URL, json={
        "customer_name": "Siti",
        "agent_name": "Wisnu",
        "conversation_history": [
            {"q": "greeting", "a": "Ya, benar", "goal": "greeting_identity"},
            {"q": "service status", "a": "Tidak ada gangguan", "goal": "service_status"},
            {"q": data['question'], "a": "Tertarik", "goal": "payment_status_info"}
        ],
        "mode": "winback"
    })
    data = response.json()
    print(f"\nAfter 'Tertarik' → Goal: {data['current_goal']}")
    assert data['current_goal'] == "payment_timing"
    
    print("\n✅ BRANCH C TEST PASSED (API)")

def test_winback_goals_count():
    """Test jumlah goals winback"""
    print_header("TEST WINBACK GOALS COUNT")
    
    response = requests.post(API_URL, json={
        "customer_name": "Test",
        "agent_name": "Agent",
        "conversation_history": [],
        "mode": "winback"
    })
    data = response.json()
    
    # Check goal_status has 15 goals
    goal_status = data.get('goal_status', {})
    total_goals = goal_status.get('total_goals', 0)
    
    print(f"Total Winback Goals: {total_goals}")
    assert total_goals == 15, f"Expected 15 goals, got {total_goals}"
    
    print("✅ Goal count validated: 15 goals")

if __name__ == "__main__":
    try:
        print("\n" + "="*60)
        print("  QUICK WINBACK API TEST")
        print("  Make sure FastAPI server is running on port 8000")
        print("="*60)
        
        # Test goals count
        test_winback_goals_count()
        
        # Test Branch A
        test_winback_branch_a()
        
        # Test Branch C
        test_winback_branch_c()
        
        print("\n" + "="*60)
        print("  ✅ ALL API TESTS PASSED!")
        print("  Winback mode working correctly via API")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("Make sure FastAPI server is running: uvicorn app.main:app --reload")
        print("Default URL: http://localhost:8000\n")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
