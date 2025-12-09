"""Test llama3 speed optimization with caching and keep-alive"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from app.services.winback_services import generate_question
import time

print("🧪 Testing llama3 speed with KEEP-ALIVE + CACHING")
print("="*70)

# Test 1: First call (cold start - will be slow)
print("\n📌 Test 1: First call (cold start)")
hist = [{'q': 'Greeting', 'a': 'Ya, pemilik', 'goal': 'greeting_identity'}]

start = time.time()
q1 = generate_question(hist)
t1 = time.time() - start

print(f"⏱️  Time: {t1:.1f}s")
print(f"🎯 Goal: {q1.get('goal')}")
print(f"❓ Question: {q1.get('question')[:60]}...")

# Test 2: Second call (should be faster - model in memory)
print("\n📌 Test 2: Second call (model already loaded)")
hist2 = [{'q': 'Greeting', 'a': 'Ya, benar', 'goal': 'greeting_identity'}]

start = time.time()
q2 = generate_question(hist2)
t2 = time.time() - start

print(f"⏱️  Time: {t2:.1f}s")
print(f"🎯 Goal: {q2.get('goal')}")
print(f"❓ Question: {q2.get('question')[:60]}...")

# Test 3: Third call with same goal (should use cache - instant!)
print("\n📌 Test 3: Third call - same goal (should hit cache)")
hist3 = [{'q': 'Greeting', 'a': 'Ya saya', 'goal': 'greeting_identity'}]

start = time.time()
q3 = generate_question(hist3)
t3 = time.time() - start

print(f"⏱️  Time: {t3:.1f}s")
print(f"🎯 Goal: {q3.get('goal')}")
print(f"❓ Question: {q3.get('question')[:60]}...")

# Summary
print("\n" + "="*70)
print("📊 PERFORMANCE SUMMARY")
print("="*70)
print(f"1st call (cold):        {t1:>6.1f}s")
print(f"2nd call (warm):        {t2:>6.1f}s  {'✅ FASTER!' if t2 < t1 else ''}")
print(f"3rd call (cached):      {t3:>6.1f}s  {'✅ INSTANT!' if t3 < 1 else ''}")

if t2 < t1 * 0.5:
    print("\n🎉 SUCCESS! Keep-alive working - 2nd call is >50% faster!")
if t3 < 0.5:
    print("🎉 SUCCESS! Cache working - 3rd call is instant!")

