import requests
import json

BASE_URL = "http://localhost:8000/api/v1/endpoints/conversation"

print("="*60)
print("🔍 DEBUG: Testing wrong number detection")
print("="*60)

conversation = []

# Step 1: Greeting
print("\n[1] Initial Greeting")
response = requests.post(
    f"{BASE_URL}/generate-simulation-questions",
    json={
        "customer_id": "DEBUG123",
        "topic": "winback",
        "conversation": conversation
    }
)
result = response.json()
print(f"✓ Q: {result['question'][:80]}")

conversation.append({
    "q": result['question'],
    "a": "Bukan, salah sambung"
})

# Step 2: Wrong number check
print("\n[2] Wrong Number Check (after 'Bukan, salah sambung')")
response = requests.post(
    f"{BASE_URL}/generate-simulation-questions",
    json={
        "customer_id": "DEBUG123",
        "topic": "winback",
        "conversation": conversation
    }
)
result = response.json()
print(f"✓ Q: {result['question'][:80]}")
print(f"  Options: {result['options']}")

conversation.append({
    "q": result['question'],
    "a": "Nomor salah"
})

# Step 3: Should trigger closing
print("\n[3] After 'Nomor salah' → SHOULD CLOSE")
print(f"📋 Conversation history being sent:")
for i, conv in enumerate(conversation, 1):
    print(f"  {i}. Q: {conv['q'][:60]}")
    print(f"     A: {conv['a']}")

response = requests.post(
    f"{BASE_URL}/generate-simulation-questions",
    json={
        "customer_id": "DEBUG123",
        "topic": "winback",
        "conversation": conversation
    }
)
result = response.json()
print(f"\n📥 Result:")
print(f"  Question: {result['question']}")
print(f"  Options: {result.get('options', [])}")
print(f"  Is Closing: {result.get('is_closing', False)}")
print(f"  Goal: {result.get('goal', 'N/A')}")

if result.get('is_closing'):
    print("\n✅ SUCCESS: Conversation correctly closed!")
else:
    print("\n❌ FAILED: Should be closing but got regular question")
    print(f"\n🔍 Check backend logs for:")
    print(f"  - [WRONG_NUMBER_CHECK] logs")
    print(f"  - Answer detection: 'Nomor salah'")
    print(f"  - Next goal determination")

print("\n" + "="*60)
