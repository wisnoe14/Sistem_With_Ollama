#!/usr/bin/env python3
import sys
sys.path.append('backend')
from app.services.gpt_service import analyze_sentiment_and_intent

text = 'Besok pasti saya bayar'
print('🔍 Testing different goal contexts:')
print()

goals = ['', 'payment_timeline', 'payment_barrier', 'status_contact']
for goal in goals:
    sentiment = analyze_sentiment_and_intent(text, goal)
    goal_label = goal if goal else '(empty)'
    print(f'Goal: {goal_label:15} -> Intent: {sentiment["intent"]:20} Confidence: {sentiment["confidence"]}%')