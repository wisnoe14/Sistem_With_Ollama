"""
Test script untuk debug device_location flow di retention mode
"""
import sys
sys.path.insert(0, 'backend')

from app.services import gpt_service

# Simulasi conversation sampai device_location
conversation_history = [
    {
        "goal": "greeting_identity",
        "q": "Apakah saya berbicara dengan Bapak/Ibu pemilik nomor ini?",
        "a": "Ya, saya pemiliknya"
    },
    {
        "goal": "service_check",
        "q": "Baik Bapak/Ibu, kami melihat layanan ICONNET Bapak/Ibu sedang terputus. Apakah ada kendala yang bisa kami bantu?",
        "a": "Ya, ada kendala"
    },
    {
        "goal": "promo_permission",
        "q": "Baik, boleh saya sampaikan promo menarik untuk Bapak/Ibu?",
        "a": "Boleh"
    },
    {
        "goal": "promo_detail",
        "q": "Kami memiliki promo diskon 20%, 25%, dan 30% untuk pelanggan setia. Apakah Bapak/Ibu tertarik?",
        "a": "Silakan dijelaskan"
    },
    {
        "goal": "activation_interest",
        "q": "Apakah Bapak/Ibu berminat untuk mengaktifkan kembali layanan ICONNET?",
        "a": "Tidak berminat"
    },
    {
        "goal": "rejection_reason",
        "q": "Boleh kami tahu apa alasan Bapak/Ibu tidak berminat?",
        "a": "Karena saya mau pindah rumah"
    },
    {
        "goal": "device_location",
        "q": "Untuk perangkat ICONNET (modem dan ONT), apakah masih berada di lokasi Bapak/Ibu?",
        "a": "Masih ada di sini"
    }
]

print("=" * 80)
print("TEST: Device Location Flow Debug")
print("=" * 80)

# Check goals status
print("\n1. Checking goal status...")
goal_status = gpt_service.check_retention_goals(conversation_history)
print(f"\nGoal Status Summary:")
print(f"  - Total goals: {goal_status.get('total_goals')}")
print(f"  - Achieved: {len(goal_status.get('achieved_goals', []))}")
print(f"  - Achievement %: {goal_status.get('achievement_percentage', 0):.1f}%")
print(f"\nAchieved Goals: {goal_status.get('achieved_goals', [])}")
print(f"\ndevice_location status: {goal_status.get('device_location', {})}")
print(f"relocation_interest status: {goal_status.get('relocation_interest', {})}")

# Determine next goal
print("\n2. Determining next goal...")
next_goal = gpt_service.determine_retention_next_goal(conversation_history, goal_status)
print(f"\n✅ Next Goal: {next_goal}")

# Generate question
print("\n3. Generating question for next goal...")
result = gpt_service.generate_question("retention", conversation_history)
print(f"\n📝 Generated Question:")
print(f"  Goal: {result.get('goal')}")
print(f"  Question: {result.get('question')}")
print(f"  Options: {result.get('options')}")

print("\n" + "=" * 80)
print("EXPECTED BEHAVIOR:")
print("  - device_location should be marked as ACHIEVED")
print("  - Next goal should be: relocation_interest")
print("  - Question should ask about 'berminat memasang di lokasi baru'")
print("=" * 80)
