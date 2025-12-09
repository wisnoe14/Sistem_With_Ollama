import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from app.services.winback_services import generate_question

print("=== Test Flow 2: gangguan → pertimbangkan → response_handling → closing ===\n")

hist = []

# Step 1: greeting_identity
q = generate_question(hist)
print(f"1. Goal: {q['goal']}")
print(f"   Question: {q['question'][:50]}...")
hist.append({'q': q['question'], 'a': 'Ya, benar', 'goal': q['goal']})

# Step 2: check_status
q = generate_question(hist)
print(f"\n2. Goal: {q['goal']}")
print(f"   Question: {q['question'][:50]}...")
hist.append({'q': q['question'], 'a': 'Ada gangguan', 'goal': q['goal']})

# Step 3: complaint_check
q = generate_question(hist)
print(f"\n3. Goal: {q['goal']}")
print(f"   Question: {q['question'][:50]}...")
hist.append({'q': q['question'], 'a': 'Masih pertimbangkan dulu', 'goal': q['goal']})

# Step 4: response_handling
q = generate_question(hist)
print(f"\n4. Goal: {q['goal']}")
print(f"   Question: {q['question'][:50]}...")
hist.append({'q': q['question'], 'a': 'Tidak ada', 'goal': q['goal']})

# Step 5: closing
q = generate_question(hist)
print(f"\n5. Goal: {q['goal']}")
print(f"   Question: {q['question'][:50]}...")

print("\n✅ Test completed!")
