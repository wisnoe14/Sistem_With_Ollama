#!/usr/bin/env python3

from app.services.gpt_service import generate_question, analyze_sentiment_and_intent

print('🧪 TESTING: New Payment Logic System')
print('='*60)

# Test 1: Positive payment intent (should go directly to closing)
print('\n📝 TEST 1: Positive Payment Intent - "Sudah bayar"')
conversation1 = [
    {'question': 'Pembayaran sudah selesai?', 'answer': 'Sudah bayar', 'goal': 'status_contact'}
]

result1 = generate_question('telecollection', conversation1)
print(f'✅ Goal: {result1.get("goal", "unknown")}')
print(f'✅ Is Closing: {result1.get("is_closing", False)}')
print(f'✅ Question: {result1.get("question", "N/A")[:80]}...')

# Test 2: Negative payment intent (should continue to payment_barrier)
print('\n📝 TEST 2: Negative Payment Intent - "Belum bayar"')  
conversation2 = [
    {'question': 'Pembayaran sudah selesai?', 'answer': 'Belum bayar', 'goal': 'status_contact'}
]

result2 = generate_question('telecollection', conversation2)
print(f'❌ Goal: {result2.get("goal", "unknown")}')
print(f'❌ Is Closing: {result2.get("is_closing", False)}')
print(f'❌ Question: {result2.get("question", "N/A")[:80]}...')

# Test 3: First question (no conversation history)
print('\n📝 TEST 3: First Question (No History)')
result3 = generate_question('telecollection', [])
print(f'🆕 Goal: {result3.get("goal", "unknown")}')
print(f'🆕 Is Closing: {result3.get("is_closing", False)}')
print(f'🆕 Question: {result3.get("question", "N/A")[:80]}...')

print('\n✅ All tests completed!')
print('='*60)