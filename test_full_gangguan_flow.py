import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from app.services.winback_services import generate_question

print("=== Test Full Flow: gangguan → complaint_apology → complaint_resolution → program_confirmation → closing ===\n")

hist = []

# Step 1: greeting_identity
q = generate_question(hist)
print(f"1. {q['goal']}")
hist.append({'q': q['question'], 'a': 'Ya, benar'})

# Step 2: service_status
q = generate_question(hist)
print(f"2. {q['goal']}")
hist.append({'q': q['question'], 'a': 'Ada gangguan'})

# Step 3: complaint_apology
q = generate_question(hist)
print(f"3. {q['goal']}")
expected_3 = 'complaint_apology'
assert q['goal'] == expected_3, f"Expected {expected_3}, got {q['goal']}"
hist.append({'q': q['question'], 'a': 'Sudah pernah lapor'})

# Step 4: complaint_resolution
q = generate_question(hist)
print(f"4. {q['goal']}")
expected_4 = 'complaint_resolution'
assert q['goal'] == expected_4, f"Expected {expected_4}, got {q['goal']}"
hist.append({'q': q['question'], 'a': 'Sudah diperbaiki'})

# Step 5: program_confirmation
q = generate_question(hist)
print(f"5. {q['goal']}")
expected_5 = 'program_confirmation'
assert q['goal'] == expected_5, f"Expected {expected_5}, got {q['goal']}"
hist.append({'q': q['question'], 'a': 'Ya, tertarik'})

# Step 6: closing_thanks
q = generate_question(hist)
print(f"6. {q['goal']}")

print(f"\n{'='*60}")
if q['goal'] in ['closing', 'closing_thanks'] or q.get('is_closing'):
    print("✅ SUCCESS: Flow correctly reaches closing")
    print("✅ Path: greeting → service_status → complaint_apology → complaint_resolution → program_confirmation → closing")
else:
    print(f"❌ FAILED: Expected closing, got {q['goal']}")
print('='*60)
