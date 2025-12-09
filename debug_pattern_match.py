"""
Simpler debug: Print EVERY condition evaluation for conversation item 5
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Just check the 5th conversation item
question = "Dengan promo yang kami tawarkan, apakah Bapak/Ibu berminat untuk mengaktifkan kembali layanan ICONNET?"
question_lower = question.lower()

print(f"Question: {question}")
print(f"Question (lower): {question_lower}")
print()

patterns = {
    "greeting_identity": ["perkenalkan saya", "dengan siapa saat ini saya berbicara", "nama pelanggan", "saya dari iconnet", "apakah benar saya terhubung"],
    "service_check": ["layanan iconnet bapak/ibu dalam kondisi", "terputus", "layanan sedang terputus", "layanan sudah aktif kembali"],
    "promo_permission": ["boleh saya sampaikan", "ada promo", "program promo", "informasi promo", "tawaran khusus", "program retention"],
    "promo_detail": ["diskon 20%", "diskon 25%", "diskon 30%", "pelanggan loyal", "kami punya program", "program khusus", "promo retention", "potongan harga", "benefit"],
    "activation_interest": ["berminat untuk mengaktifkan kembali", "dengan promo yang kami tawarkan", "tertarik untuk melanjutkan", "bersedia mengaktifkan kembali", "apakah berminat", "minat untuk aktifkan", "lanjutkan layanan"]
}

for goal, patterns_list in patterns.items():
    matched = any(phrase in question_lower for phrase in patterns_list)
    if matched:
        matching_phrases = [p for p in patterns_list if p in question_lower]
        print(f"✅ {goal}: MATCH - phrases: {matching_phrases}")
    else:
        print(f"❌ {goal}: NO MATCH")
