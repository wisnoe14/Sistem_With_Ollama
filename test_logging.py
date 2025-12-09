#!/usr/bin/env python3

import requests
import json

# Test server running on localhost:8000
BASE_URL = "http://localhost:8000/api/v1"

def test_process_answer_logging():
    """Test the process-answer endpoint with enhanced logging"""
    print("=== Testing Process Answer Logging ===\n")
    
    # Test data - telecollection conversation
    test_data = {
        "customer_id": "ICON12345",
        "cs_name": "Sarah",
        "topic": "telecollection",
        "conversation": [
            {"q": "Halo Pak John, selamat pagi! Saya Sarah dari ICONNET. Gimana kabarnya hari ini? Oh iya, saya mau tanya nih, untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?", "a": "Halo, kabar baik. Maaf ya, saya masih ada kendala keuangan sedikit."}
        ],
        "manual_input": "Saya paham situasinya. Kira-kira kapan estimasi bisa bayar?"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/process-answer", json=test_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Check server terminal for detailed logs")
            print(f"Next Question: {result.get('next_question', 'N/A')}")
            print(f"Goals Progress: {result.get('goals_progress', {})}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

def test_generate_simulation_logging():
    """Test the generate-simulation-questions endpoint with enhanced logging"""
    print("\n=== Testing Generate Simulation Logging ===\n")
    
    # Test data - new conversation
    test_data = {
        "customer_id": "ICON12345",
        "topic": "telecollection", 
        "user": "sarah@iconnet.com",
        "conversation": []
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-simulation-questions", json=test_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Check server terminal for detailed logs")
            print(f"Question: {result.get('question', 'N/A')}")
            print(f"Options: {result.get('options', [])}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    # Test logging enhancements
    test_generate_simulation_logging()
    test_process_answer_logging()
    
    print("\n🔍 Check the server terminal output for comprehensive conversation logs!")
    print("The terminal should show:")
    print("- Customer and CS information")
    print("- Conversation history") 
    print("- Goal progress with detailed scores")
    print("- Next question generation details")