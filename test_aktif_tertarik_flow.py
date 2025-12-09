import sys
sys.path.append('backend')
from app.services.gpt_service import generate_question

print("=== Test Flow 4: masih aktif → promo → tertarik → payment → closing ===\n")

hist = []

# Step 1: greeting_identity
q = generate_question('winback', hist)
print(f"1. Goal: {q['goal']}")
hist.append({'q': q['question'], 'a': 'Ya, benar', 'goal': q['goal']})

# Step 2: check_status
q = generate_question('winback', hist)
print(f"2. Goal: {q['goal']}")
hist.append({'q': q['question'], 'a': 'Masih aktif', 'goal': q['goal']})

# Step 3: promo_offer
q = generate_question('winback', hist)
print(f"3. Goal: {q['goal']}")
hist.append({'q': q['question'], 'a': 'Tertarik', 'goal': q['goal']})

# Step 4: payment_confirmation
q = generate_question('winback', hist)
print(f"4. Goal: {q['goal']}")
hist.append({'q': q['question'], 'a': 'Besok', 'goal': q['goal']})

# Step 5: closing
q = generate_question('winback', hist)
print(f"5. Goal: {q['goal']}")

print("\n✅ Test completed!")
