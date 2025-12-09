"""
Test script to debug activation_interest loop issue
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.retention_services import (
    check_goals as check_retention_goals,
    determine_next_goal as determine_retention_next_goal,
)

# Simulate conversation where user says "Tidak berminat"
conversation_history = [
    {
        "q": "Halo Budi! Selamat pagi, saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Budi?",
        "a": "Ya, benar"
    },
    {
        "q": "Baik Bapak/Ibu, kami lihat layanan ICONNET Bapak/Ibu dalam kondisi terputus. Apakah benar demikian?",
        "a": "Ya, terputus"
    },
    {
        "q": "Baik Bapak/Ibu, kami ada promo menarik untuk pelanggan loyal. Boleh saya sampaikan informasinya?",
        "a": "Boleh"
    },
    {
        "q": "Kami punya program khusus: diskon 20% untuk pelanggan loyal, 25% untuk pelanggan setia, dan 30% untuk pelanggan istimewa. Promo ini tersedia terbatas.",
        "a": "Tidak tertarik"
    },
    {
        "q": "Dengan promo yang kami tawarkan, apakah Bapak/Ibu berminat untuk mengaktifkan kembali layanan ICONNET?",
        "a": "Tidak berminat"
    }
]

print("=" * 60)
print("TEST: Activation Interest Loop Debug")
print("=" * 60)
print()

print("Conversation History:")
for i, conv in enumerate(conversation_history, 1):
    print(f"   {i}. Q: {conv['q'][:80]}...")
    print(f"      A: {conv['a']}")
print()

# Check goals
goal_status = check_retention_goals(conversation_history)

print()
print(f"Achieved Goals: {goal_status['achieved_goals']}")
print(f"Missing Goals: {goal_status['missing_goals']}")
print()

# Determine next goal
next_goal = determine_retention_next_goal(conversation_history)

print()
print(f"Next Goal: {next_goal}")
print()

# Check if activation_interest is marked as achieved
activation_achieved = goal_status.get('activation_interest', {}).get('achieved', False)
print(f"activation_interest achieved: {activation_achieved}")
print()

# Expected behavior
if activation_achieved:
    print("PASS: activation_interest correctly marked as achieved")
    if next_goal != "activation_interest":
        print(f"PASS: Next goal is not activation_interest (it's {next_goal})")
    else:
        print(f"FAIL: Next goal is still activation_interest - LOOP DETECTED!")
else:
    print("FAIL: activation_interest NOT marked as achieved - will cause loop!")
