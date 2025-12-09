#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test winback sentiment-based answer generation"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.goal_utils import generate_automatic_customer_answer

# Test question with various sentiment options
test_question = {
    'id': 'wb_003',
    'question': 'Apakah Bapak/Ibu bersedia untuk mengaktifkan layanan ICONNET kembali?',
    'options': [
        'Ya, bersedia',  # Positive
        'Tidak, terima kasih',  # Negative
        'Pertimbangkan dulu',  # Neutral
        'Ada kendala'  # Neutral
    ]
}

print("=" * 60)
print("TEST WINBACK SENTIMENT-BASED ANSWER GENERATION")
print("=" * 60)
print(f"\nQuestion: {test_question['question']}")
print(f"\nOptions:")
for i, opt in enumerate(test_question['options'], 1):
    print(f"  {i}. {opt}")

print("\n" + "-" * 60)
print("Testing 10x dengan rule_based mode:")
print("-" * 60)

results = {
    'positive': 0,
    'negative': 0,
    'neutral': 0
}

for i in range(10):
    answer = generate_automatic_customer_answer(test_question, "rule_based")
    print(f"{i+1:2d}. {answer}")
    
    # Count sentiment distribution
    if answer == 'Ya, bersedia':
        results['positive'] += 1
    elif answer == 'Tidak, terima kasih':
        results['negative'] += 1
    else:
        results['neutral'] += 1

print("\n" + "=" * 60)
print("DISTRIBUTION (Expected: ~40% positive, ~30% neutral, ~30% negative):")
print("=" * 60)
print(f"Positive: {results['positive']}/10 ({results['positive']*10}%)")
print(f"Negative: {results['negative']}/10 ({results['negative']*10}%)")
print(f"Neutral:  {results['neutral']}/10 ({results['neutral']*10}%)")
print("=" * 60)
