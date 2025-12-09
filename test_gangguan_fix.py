import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from app.services.winback_services import generate_question

print("=== Test: check_status (gangguan) should go to complaint_check ===\n")

hist = []

# Step 1: greeting_identity
q = generate_question(hist)
print(f"1. Goal: {q['goal']}")
hist.append({'q': q['question'], 'a': 'Ya, benar'})

# Step 2: check_status
q = generate_question(hist)
print(f"2. Goal: {q['goal']}")
print(f"   Q: {q['question'][:60]}...")
hist.append({'q': q['question'], 'a': 'Ada gangguan'})

# Step 3: Should be complaint_check
q = generate_question(hist)
print(f"3. Goal: {q['goal']}")
print(f"   Q: {q['question'][:60]}...")

print(f"\n{'='*60}")
if q['goal'] == 'complaint_check':
    print("✅ SUCCESS: Flow correctly routes to complaint_check")
else:
    print(f"❌ FAILED: Expected complaint_check, got {q['goal']}")
print('='*60)
