import sys
sys.path.append('backend')
from app.services.gpt_service import generate_question

print("=== Debug: promo_offer branching issue ===\n")

hist = []

# Step 1: greeting_identity
q = generate_question('winback', hist)
print(f"1. {q['goal']}")
hist.append({'q': q['question'], 'a': 'Ya, benar'})

# Step 2: check_status
q = generate_question('winback', hist)
print(f"2. {q['goal']}")
print(f"   Q: {q['question']}")
hist.append({'q': q['question'], 'a': 'Masih aktif'})

# Step 3: promo_offer
q = generate_question('winback', hist)
print(f"3. {q['goal']}")
print(f"   Q: {q['question']}")
hist.append({'q': q['question'], 'a': 'Tertarik'})

# Step 4: Should be payment_confirmation
print("\n[DEBUG] Checking conversation history:")
for i, conv in enumerate(hist):
    print(f"  {i+1}. Q: {conv['q'][:60]}")
    print(f"     A: {conv['a']}")

q = generate_question('winback', hist)
print(f"\n4. Goal: {q['goal']}")
print(f"   Expected: payment_confirmation")
print(f"   Actual: {q['goal']}")
