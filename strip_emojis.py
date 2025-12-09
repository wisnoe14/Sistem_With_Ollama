#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick script to remove emoji from gpt_service.py for Windows console compatibility"""
import re

filepath = r'backend\app\services\gpt_service.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove emojis and arrows
cleaned = re.sub(r'[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF\u2B50\u2705\u2753\u26A0\uFE0F\u2190-\u21FF]', '', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(cleaned)

print("OK: Emojis and arrows removed from gpt_service.py")
