#!/usr/bin/env python3
"""
Test winback prediction with the conversation from user's log
"""

import sys
import os
sys.path.append('backend')

from app.services.gpt_service import predict_winback_outcome

print("🧪 TESTING WINBACK PREDICTION FIXES")
print("=" * 60)

# Recreate the conversation from user's log
test_conversation = [
    {"q": "Status Dihubungi?", "a": "Dihubungi"},
    {"q": "Selamat sore, Bapak/Ibu. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Budi?", "a": "Ya, benar"},
    {"q": "Sebagai bentuk apresiasi, kami menawarkan promo gratis 1 bulan untuk Bapak/Ibu jika bersedia mengaktifkan layanan ICONNET kembali. Promo ini bisa Bapak/Ibu dapatkan dengan cara melakukan 1x pembayaran untuk mengaktifkan layanan ICONNETnya. Apakah Bapak/Ibu bersedia untuk mengaktifkan layanan ICONNETnya kembali?", "a": "Pertimbangkan dulu"},
    {"q": "Terima kasih, Bapak/Ibu. Kami melihat bahwa layanan ICONNET Bapak/Ibu sedang terputus, dan kami ingin tahu apakah ada kendala yang bisa kami bantu? Saat ini kami sedang memiliki promo menarik untuk Bapak/Ibu. Apakah boleh saya sampaikan lebih lanjut?", "a": "Tidak tertarik"},
    {"q": "Baik Bapak/Ibu, jika boleh tahu karena apa ya tidak bersedia mengaktifkan kembali?", "a": "gangguan jaringan terus"},
    {"q": "Baik, mohon maaf atas ketidaknyamanannya, akan kami teruskan ke tim terkait ya Bapak/Ibu. Apakah dengan perbaikan layanan dan promo gratis 1 bulan, Bapak/Ibu bersedia mencoba lagi?", "a": "Ya, mau coba lagi"},
    {"q": "Baik Bapak/Ibu, akan kami bantu untuk mengirimkan kode pembayaran melalui email. Untuk estimasi pembayaran akan dibayarkan berapa jam ke depan ya?", "a": "lagi seminggu"},
    {"q": "Baik Bapak/Ibu, untuk perangkat ICONNET-nya apakah masih berada di lokasi rumah?", "a": "Sudah dikembalikan"}
]

print("📋 Testing conversation analysis:")
print("   - Identity confirmed: Ya, benar")  
print("   - Initial response: Pertimbangkan dulu")
print("   - Reason: gangguan jaringan terus")
print("   - Final decision: Ya, mau coba lagi")
print("   - Timeline: lagi seminggu")
print("   - Equipment: Sudah dikembalikan")

print(f"\n🔍 RUNNING PREDICTION...")

try:
    result = predict_winback_outcome(test_conversation)
    
    print(f"\n📊 PREDICTION RESULTS:")
    print(f"   Status: {result.get('status_dihubungi', 'Unknown')}")
    print(f"   Keputusan: {result.get('keputusan', 'Unknown')}")
    print(f"   Probability: {result.get('probability', 0)}%")
    print(f"   Confidence: {result.get('confidence', 'Unknown')}")
    print(f"   Alasan: {result.get('alasan', 'No reason')}")
    
    detail = result.get('detail_analysis', {})
    print(f"\n📈 DETAIL ANALYSIS:")
    print(f"   Interest Score: {detail.get('interest_score', 0):.1f}")
    print(f"   Commitment Score: {detail.get('commitment_score', 0):.1f}")
    print(f"   Cooperation Rate: {detail.get('cooperation_rate', 0):.1f}%")
    print(f"   Objection Count: {detail.get('objection_count', 0)}")
    print(f"   Price Sensitivity: {detail.get('price_sensitivity', 0)}")
    
    print(f"\n✅ PREDICTION ANALYSIS:")
    print(f"   - Equipment 'Sudah dikembalikan' should NOT be treated as payment")
    print(f"   - 'Ya, mau coba lagi' should indicate strong interest")
    print(f"   - Timeline 'lagi seminggu' shows commitment")
    print(f"   - Should predict BERHASIL REAKTIVASI or similar positive outcome")
    
except Exception as e:
    print(f"❌ ERROR in prediction: {e}")
    import traceback
    traceback.print_exc()

print(f"\n🎉 WINBACK PREDICTION TEST COMPLETED!")