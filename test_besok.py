#!/usr/bin/env python3
import sys
sys.path.append('backend')
from app.services.gpt_service import analyze_sentiment_and_intent

# Test dengan goal kosong (seperti di conversation real)
text = 'Besok'
sentiment = analyze_sentiment_and_intent(text, '')
print(f'Text: "{text}"')
print(f'Goal: (empty)')
print(f'Intent: {sentiment["intent"]}')
print(f'Confidence: {sentiment["confidence"]}%')
print(f'Sentiment: {sentiment["sentiment"]}')