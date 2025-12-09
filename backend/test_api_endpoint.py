#!/usr/bin/env python3

import requests
import json

# Test generate-simulation-questions endpoint
print('🧪 Testing API endpoints...')
print('='*50)

url = 'http://localhost:8000/api/conversation/generate-simulation-questions'
data = {
    'customer_id': 'ICON12',
    'topic': 'telecollection',
    'conversation': [],
    'user': 'test@test.com'
}

try:
    response = requests.post(url, json=data, timeout=10)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        print(f'✅ Question Generated Successfully')
        print(f'Question: {result.get("question", "N/A")[:80]}...')
        print(f'Options: {result.get("options", [])}')
        print(f'Is Closing: {result.get("is_closing", False)}')
    else:
        print(f'❌ Error: {response.text}')
except Exception as e:
    print(f'❌ Request failed: {e}')

print('\n' + '='*50)