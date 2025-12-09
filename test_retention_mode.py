"""
Test Retention Mode - Complete Flow Testing

Test scenario untuk retention mode dengan berbagai alur:
1. Happy Path: Customer interested → payment_timing → closing
2. Rejection Path: Not interested → reason_inquiry → device_check → closing
3. Complaint Path: Has complaint → complaint_handling → commitment_check → closing
4. Skip Promo Path: Don't want promo → reason_inquiry → device_check → closing
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1/endpoints"

def test_retention_flow(conversation_id: str, flow_type: str = "happy"):
    """
    Test retention flow dengan berbagai skenario
    
    Args:
        conversation_id: ID conversation
        flow_type: "happy", "rejection", "complaint", "skip_promo"
    """
    print(f"\n{'='*80}")
    print(f"🎯 TESTING RETENTION FLOW: {flow_type.upper()}")
    print(f"{'='*80}\n")
    
    # Scenario mapping
    scenarios = {
        "happy": [
            ("Selamat siang, perkenalkan saya Rina dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu [Nama Pelanggan]?", "Ya, benar"),
            ("Baik, terima kasih konfirmasinya. Saya ingin menanyakan mengenai layanan ICONNET Bapak/Ibu yang terputus. Apakah ada kendala yang bisa kami bantu?", "Kendala biaya saja"),
            ("Baik, saya pahami. Kebetulan kami ada promo menarik untuk pelanggan setia seperti Bapak/Ibu. Boleh saya sampaikan promonya?", "Boleh, sampaikan"),
            ("Kami ada promo menarik: Diskon 20% untuk pembayaran bulanan, Diskon 25% untuk 6 bulan, atau Diskon 30% untuk 12 bulan. Apakah Bapak/Ibu bersedia untuk mengaktifkan kembali layanan ICONNET dengan promo ini?", "Bersedia"),
            ("Terima kasih atas keputusannya. Kira-kira kapan Bapak/Ibu bisa melakukan pembayaran untuk mengaktifkan layanan kembali?", "Hari ini juga"),
            ("Baik, terima kasih. Tim kami akan menghubungi untuk koordinasi pembayaran. Semoga layanan ICONNET terus memuaskan!", "Terima kasih")
        ],
        "rejection": [
            ("Selamat siang, perkenalkan saya Rina dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu [Nama Pelanggan]?", "Ya, benar"),
            ("Baik, terima kasih konfirmasinya. Saya ingin menanyakan mengenai layanan ICONNET Bapak/Ibu yang terputus. Apakah ada kendala yang bisa kami bantu?", "Tidak ada kendala"),
            ("Baik, saya pahami. Kebetulan kami ada promo menarik untuk pelanggan setia seperti Bapak/Ibu. Boleh saya sampaikan promonya?", "Boleh"),
            ("Kami ada promo menarik: Diskon 20% untuk pembayaran bulanan, Diskon 25% untuk 6 bulan, atau Diskon 30% untuk 12 bulan. Apakah Bapak/Ibu bersedia untuk mengaktifkan kembali layanan ICONNET dengan promo ini?", "Tidak berminat"),
            ("Baik, boleh saya tahu karena apa tidak berminat dengan promo ini?", "Pindah rumah"),
            ("Baik, saya pahami. Apakah perangkat ICONNET masih ada di rumah Bapak/Ibu?", "Masih ada"),
            ("Terima kasih atas informasinya. Jika ada kebutuhan di lokasi baru, silakan hubungi kami kembali.", "Terima kasih")
        ],
        "complaint": [
            ("Selamat siang, perkenalkan saya Rina dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu [Nama Pelanggan]?", "Ya"),
            ("Baik, terima kasih konfirmasinya. Saya ingin menanyakan mengenai layanan ICONNET Bapak/Ibu yang terputus. Apakah ada kendala yang bisa kami bantu?", "Sering gangguan"),
            ("Baik, saya pahami. Kebetulan kami ada promo menarik untuk pelanggan setia seperti Bapak/Ibu. Boleh saya sampaikan promonya?", "Boleh"),
            ("Kami ada promo menarik: Diskon 20% untuk pembayaran bulanan, Diskon 25% untuk 6 bulan, atau Diskon 30% untuk 12 bulan. Apakah Bapak/Ibu bersedia untuk mengaktifkan kembali layanan ICONNET dengan promo ini?", "Tidak, karena sering rusak"),
            ("Baik, boleh saya tahu karena apa tidak berminat dengan promo ini?", "Gangguan terus, lambat"),
            ("Baik, saya pahami keluhannya. Apakah Bapak/Ibu sudah pernah melapor ke CS kami sebelumnya?", "Sudah pernah tapi tidak ada perbaikan"),
            ("Saya minta maaf atas ketidaknyamanan ini. Jika gangguannya teratasi, apakah Bapak/Ibu bersedia lanjut berlangganan?", "Tidak bersedia"),
            ("Baik, saya pahami keputusannya. Apakah perangkat ICONNET masih ada di rumah?", "Masih ada"),
            ("Terima kasih atas informasinya. Kami akan terus memperbaiki layanan kami.", "Terima kasih")
        ],
        "skip_promo": [
            ("Selamat siang, perkenalkan saya Rina dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu [Nama Pelanggan]?", "Ya"),
            ("Baik, terima kasih konfirmasinya. Saya ingin menanyakan mengenai layanan ICONNET Bapak/Ibu yang terputus. Apakah ada kendala yang bisa kami bantu?", "Tidak ada"),
            ("Baik, saya pahami. Kebetulan kami ada promo menarik untuk pelanggan setia seperti Bapak/Ibu. Boleh saya sampaikan promonya?", "Tidak usah, tidak tertarik"),
            ("Baik, boleh saya tahu alasan tidak berminat?", "Biaya mahal"),
            ("Baik, saya pahami. Apakah perangkat ICONNET masih ada di rumah?", "Sudah dikembalikan"),
            ("Terima kasih atas informasinya. Jika berubah pikiran, silakan hubungi kami kembali.", "Terima kasih")
        ]
    }
    
    if flow_type not in scenarios:
        print(f"❌ Unknown flow type: {flow_type}")
        return
    
    flow = scenarios[flow_type]
    
    for i, (expected_question, answer) in enumerate(flow, 1):
        print(f"\n--- Step {i} ---")
        
        # Get question
        response = requests.post(
            f"{BASE_URL}/generate_question",
            json={
                "conversation_id": conversation_id,
                "mode": "retention"
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get question: {response.text}")
            break
        
        result = response.json()
        question = result.get('question', '')
        options = result.get('options', [])
        goal = result.get('goal', '')
        
        print(f"📝 Goal: {goal}")
        print(f"❓ Question: {question}")
        print(f"✅ Options: {options}")
        
        # Check if question contains expected pattern (simplified check)
        # print(f"Expected pattern: {expected_question[:50]}...")
        
        # Submit answer
        print(f"💬 Answer: {answer}")
        
        submit_response = requests.post(
            f"{BASE_URL}/submit_answer",
            json={
                "conversation_id": conversation_id,
                "question": question,
                "answer": answer,
                "goal": goal,
                "mode": "retention"
            },
            timeout=30
        )
        
        if submit_response.status_code != 200:
            print(f"❌ Failed to submit answer: {submit_response.text}")
            break
        
        submit_result = submit_response.json()
        print(f"✅ Answer submitted. Status: {submit_result.get('status', 'unknown')}")
        
        # Check if conversation is complete
        if submit_result.get('conversation_complete', False):
            print(f"\n{'='*80}")
            print("🎉 CONVERSATION COMPLETE!")
            print(f"{'='*80}")
            break
        
        time.sleep(0.5)
    
    # Get final summary
    print(f"\n{'='*80}")
    print("📊 FINAL SUMMARY")
    print(f"{'='*80}")
    
    summary_response = requests.get(
        f"{BASE_URL}/conversation_summary/{conversation_id}",
        timeout=30
    )
    
    if summary_response.status_code == 200:
        summary = summary_response.json()
        print(f"✅ Total Questions: {summary.get('total_questions', 0)}")
        print(f"✅ Achievement: {summary.get('achievement_percentage', 0)}%")
        print(f"✅ Achieved Goals: {summary.get('achieved_goals', [])}")
        print(f"✅ Missing Goals: {summary.get('missing_goals', [])}")
    else:
        print(f"❌ Failed to get summary: {summary_response.text}")

def main():
    """Run all retention flow tests"""
    test_flows = ["happy", "rejection", "complaint", "skip_promo"]
    
    for i, flow in enumerate(test_flows, 1):
        conversation_id = f"retention_test_{flow}_{int(time.time())}"
        test_retention_flow(conversation_id, flow)
        
        if i < len(test_flows):
            print(f"\n{'='*80}")
            print("⏳ Waiting 2 seconds before next test...")
            print(f"{'='*80}\n")
            time.sleep(2)

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║          RETENTION MODE FLOW TESTING                           ║
    ║                                                                 ║
    ║  Testing 4 scenarios:                                          ║
    ║  1. Happy Path - Customer interested → payment → closing      ║
    ║  2. Rejection - Not interested → reason → device → closing    ║
    ║  3. Complaint - Has issue → handling → commitment → closing   ║
    ║  4. Skip Promo - Don't want promo → reason → device → closing ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    main()
