#!/usr/bin/env python3
"""Test API endpoint dengan format yang tepat"""

import requests
import json

def test_api_endpoint():
    """Test API endpoint dengan conversation format yang benar"""
    
    url = "http://localhost:8000/api/conversation/generate-simulation-questions"
    
    # Test 1: Initial conversation
    print("=== TEST 1: Initial Question ===")
    payload1 = {
        "topic": "telecollection",
        "conversation": []
    }
    
    try:
        response = requests.post(url, json=payload1, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: After positive payment answer  
    print("\n=== TEST 2: Positive Payment (Should Close) ===")
    payload2 = {
        "topic": "telecollection", 
        "conversation": [
            {
                "q": "Selamat siang Pak, saya dari ICONNET. Bagaimana kabar Bapak hari ini?",
                "a": "Baik, ada apa ya?",
                "goal": "status_contact"
            },
            {
                "q": "Saya ingin konfirmasi terkait pembayaran tagihan ICONNET Bapak bulan ini. Apakah sudah melakukan pembayaran?",
                "a": "Sudah bayar kemarin di ATM",
                "goal": "status_contact"
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload2, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result}")
            print(f"Goal: {result.get('goal', 'N/A')}")
            print(f"Is Closing: {result.get('is_closing', False)}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        
    # Test 3: After negative payment answer
    print("\n=== TEST 3: Negative Payment (Should Continue) ===")
    payload3 = {
        "topic": "telecollection",
        "conversation": [
            {
                "q": "Selamat siang Pak, saya dari ICONNET. Bagaimana kabar Bapak hari ini?", 
                "a": "Baik, ada apa ya?",
                "goal": "status_contact"
            },
            {
                "q": "Saya ingin konfirmasi terkait pembayaran tagihan ICONNET Bapak bulan ini. Apakah sudah melakukan pembayaran?",
                "a": "Belum bayar, uang lagi habis",
                "goal": "status_contact" 
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload3, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result}")
            print(f"Goal: {result.get('goal', 'N/A')}")
            print(f"Is Closing: {result.get('is_closing', False)}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_api_endpoint()