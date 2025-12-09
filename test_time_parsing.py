#!/usr/bin/env python3
"""
Test script untuk menguji parsing kata waktu menjadi tanggal spesifik
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_time_parsing():
    """Test parsing berbagai ekspres waktu"""
    
    print("🗓️ Testing Time Expression Parsing")
    print("=" * 60)
    
    try:
        from app.services.gpt_service import parse_time_expressions_to_date
        
        # Test cases dengan berbagai kata waktu
        test_expressions = [
            "Besok saya bayar",
            "Lusa baru bisa transfer",
            "Minggu depan pasti saya lunas",
            "3 hari lagi saya bayar",
            "Dalam 2 hari saya selesaikan",
            "Senin saya datang ke bank",
            "Jumat ini saya transfer",
            "Tanggal 20 saya bayar",
            "Sore ini saya transfer",
            "Sekarang juga saya bayar",
            "1 minggu lagi ya",
            "Sebulan kedepan",
            "Tidak ada waktu pasti",  # Should not detect
            "Sudah lunas kok",  # Should not detect
        ]
        
        for i, expression in enumerate(test_expressions, 1):
            print(f"\n📝 Test {i}: '{expression}'")
            
            result = parse_time_expressions_to_date(expression)
            
            if result['formatted_date']:
                print(f"✅ Detected: '{result['detected_timeframe']}'")
                print(f"📅 Target Date: {result['formatted_date']}")
                print(f"🎯 Confidence: {result['confidence']}%")
            else:
                print(f"❌ No time expression detected")
                
        print(f"\n🎯 Time Expression Parsing Test Complete!")
        
    except ImportError as e:
        print(f"⚠️  Cannot import: {e}")

def test_telecollection_with_dates():
    """Test telecollection prediction dengan parsing tanggal"""
    
    print(f"\n🎯 Testing Telecollection with Date Parsing")
    print("=" * 60)
    
    try:
        from app.services.gpt_service import generate_final_prediction
        
        test_conversations = [
            {
                "name": "Customer bilang 'besok'",
                "conversation": [
                    {"q": "Status dihubungi?", "a": "Terhubung"},
                    {"q": "Kapan Anda berencana melakukan pembayaran?", "a": "Besok saya bayar kok"}
                ]
            },
            {
                "name": "Customer bilang '3 hari lagi'",
                "conversation": [
                    {"q": "Status dihubungi?", "a": "Terhubung"},
                    {"q": "Kapan Anda berencana melakukan pembayaran?", "a": "3 hari lagi saya transfer"}
                ]
            },
            {
                "name": "Customer bilang 'minggu depan'",
                "conversation": [
                    {"q": "Status dihubungi?", "a": "Terhubung"},
                    {"q": "Kapan Anda berencana melakukan pembayaran?", "a": "Minggu depan pasti saya bayar"}
                ]
            },
            {
                "name": "Customer bilang 'senin'",
                "conversation": [
                    {"q": "Status dihubungi?", "a": "Terhubung"},
                    {"q": "Kapan Anda berencana melakukan pembayaran?", "a": "Senin saya ke bank dulu"}
                ]
            }
        ]
        
        for i, test_case in enumerate(test_conversations, 1):
            print(f"\n📋 Test {i}: {test_case['name']}")
            
            result = generate_final_prediction("telecollection", test_case['conversation'])
            
            print(f"📊 Keputusan: {result.get('keputusan', 'N/A')}")
            print(f"📝 Alasan: {result.get('alasan', 'N/A')}")
            
            # Check timeline commitments for date info
            detail_analysis = result.get('detail_analysis', {})
            timeline_commitments = detail_analysis.get('timeline_commitments', [])
            
            if timeline_commitments:
                print(f"📅 Timeline Commitments:")
                for j, commitment in enumerate(timeline_commitments):
                    time_info = commitment.get('time_parsed', {})
                    if time_info and time_info.get('formatted_date'):
                        print(f"   {j+1}. '{time_info['detected_timeframe']}' → {time_info['formatted_date']}")
            
            print("-" * 40)
            
    except ImportError as e:
        print(f"⚠️  Cannot import: {e}")

if __name__ == "__main__":
    test_time_parsing()
    test_telecollection_with_dates()