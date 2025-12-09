"""Test complaint_resolution detection"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from app.services.retention_services import check_goals as check_retention_goals

# Test complaint_resolution detection with ACTUAL questions from the log
conv = [
    {'q': 'Baik, kami akan lakukan pengecekan ulang dan pastikan kendala tersebut dapat teratasi. Jika gangguannya sudah selesai, apakah Bapak/Ibu bersedia untuk melanjutkan layanan kembali?', 'a': 'Bersedia jika selesai'},
    {'q': 'If the issue is resolved, are you willing to continue using our service?', 'a': 'tentu'},
    {'q': 'Apabila Resolusi Keluhan Selesai, Apakah Anda Bersedia Melanjutkan Layanan dengan Kami?', 'a': 'tentu'}
]

print("Testing complaint_resolution detection with REAL questions from log...")
print("\nQuestions being tested:")
for i, c in enumerate(conv, 1):
    print(f"{i}. {c['q'][:80]}...")

result = check_retention_goals(conv)
print(f"\n{'='*70}")
print(f"complaint_resolution achieved: {result.get('complaint_resolution', {}).get('achieved', False)}")
print(f"Achieved goals: {result.get('achieved_goals', [])}")
print(f"{'='*70}")

if result.get('complaint_resolution', {}).get('achieved', False):
    print("\n✅ complaint_resolution DETECTED - Loop fixed!")
else:
    print("\n❌ complaint_resolution NOT DETECTED - Loop will still occur!")
    print("\n🔍 Debug info:")
    print(f"   Question 1 (ID): {conv[0]['q'][:50]}")
    print(f"   Question 2 (EN): {conv[1]['q'][:50]}")
    print(f"   Question 3 (RK): {conv[2]['q'][:50]}")
