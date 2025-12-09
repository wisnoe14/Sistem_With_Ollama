#!/usr/bin/env python3
"""
Quick test untuk melihat preview format estimasi pembayaran dengan tanggal
"""

from datetime import datetime, timedelta

def preview_estimasi_pembayaran():
    """Preview format estimasi pembayaran yang akan ditampilkan"""
    
    print("🗓️ Preview Format Estimasi Pembayaran")
    print("=" * 50)
    
    now = datetime.now()
    
    # Telecollection scenarios
    print(f"\n📋 TELECOLLECTION Scenarios:")
    print(f"✅ SUDAH BAYAR: 'Sudah Lunas - {now.strftime('%d %B %Y')}'")
    
    target_date = now + timedelta(days=2)
    print(f"⏰ AKAN BAYAR: 'Estimasi: {target_date.strftime('%d %B %Y')} (1-3 Hari)'")
    
    target_date = now + timedelta(days=10)
    print(f"🤔 KEMUNGKINAN BAYAR: 'Estimasi: {target_date.strftime('%d %B %Y')} (7-14 Hari)'")
    
    print(f"❌ SULIT BAYAR: 'Memerlukan Follow-up Khusus - Tanggal Belum Pasti'")
    
    # Winback scenarios
    print(f"\n📋 WINBACK Scenarios:")
    activation_date = now + timedelta(days=3)
    print(f"🌟 TERTARIK REAKTIVASI: 'Target Aktivasi: {activation_date.strftime('%d %B %Y')}'")
    
    print(f"❌ TIDAK TERTARIK: 'Tidak Ada Rencana Reaktivasi'")
    
    followup_date = now + timedelta(days=7)
    print(f"🤷 KEMUNGKINAN TERTARIK: 'Follow-up: {followup_date.strftime('%d %B %Y')}'")
    
    # Retention scenarios  
    print(f"\n📋 RETENTION Scenarios:")
    review_date = now + timedelta(days=30)
    print(f"💝 LOYAL CUSTOMER: 'Review Berikutnya: {review_date.strftime('%d %B %Y')}'")
    
    urgent_date = now + timedelta(days=1)
    print(f"🚨 HIGH CHURN RISK: 'Tindakan Segera: {urgent_date.strftime('%d %B %Y')}'")
    
    monitor_date = now + timedelta(days=14)
    print(f"📊 LIKELY TO STAY: 'Monitoring: {monitor_date.strftime('%d %B %Y')}'")
    
    print(f"\n🎯 Format: DD Month YYYY (e.g., 15 October 2025)")
    print(f"📅 Tanggal hari ini: {now.strftime('%d %B %Y')}")

if __name__ == "__main__":
    preview_estimasi_pembayaran()