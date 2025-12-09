import requests
import json

# Test endpoint yang bermasalah
url = "http://localhost:8000/api/v1/endpoints/conversation/generate-simulation-questions"

payload = {
    "customer_id": "ICON12345", 
    "topic": "telecollection",
    "conversation": [
        {
            "q": "Halo, untuk pembayaran ICONNET bulan ini sudah diselesaikan belum?",
            "a": "Belum pak, lupa",
            "goal": "status_contact"
        }
    ],
    "user": "test@iconnet.id"
}

print("Testing with conversation history (second question)...")

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")