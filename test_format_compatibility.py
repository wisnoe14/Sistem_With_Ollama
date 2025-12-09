#!/usr/bin/env python3
"""Test format compatibility untuk conversation history"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gpt_service import generate_question

def test_format_compatibility():
    """Test both conversation formats"""
    
    print("=== TEST 1: Format API ({'q': ..., 'a': ...}) ===")
    
    # Format dari API endpoint
    api_conversation = [
        {'q': 'Selamat siang Pak, saya dari ICONNET. Bagaimana kabar Bapak hari ini?', 
         'a': 'Baik, ada apa ya?', 
         'goal': 'status_contact'},
        
        {'q': 'Saya ingin konfirmasi terkait pembayaran tagihan ICONNET Bapak bulan ini. Apakah sudah melakukan pembayaran?', 
         'a': 'Sudah bayar kemarin di ATM', 
         'goal': 'status_contact'}
    ]
    
    try:
        result = generate_question("telecollection", api_conversation)
        print(f"✅ Result: {result}")
        print(f"Goal: {result.get('goal', 'N/A')}")
        print(f"Is Closing: {result.get('is_closing', False)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== TEST 2: Format Backend ({'question': ..., 'answer': ...}) ===")
    
    # Format dari backend testing
    backend_conversation = [
        {'question': 'Selamat siang Pak, saya dari ICONNET. Bagaimana kabar Bapak hari ini?', 
         'answer': 'Baik, ada apa ya?', 
         'goal': 'status_contact'},
        
        {'question': 'Saya ingin konfirmasi terkait pembayaran tagihan ICONNET Bapak bulan ini. Apakah sudah melakukan pembayaran?', 
         'answer': 'Belum bayar, nanti dulu ya', 
         'goal': 'status_contact'}
    ]
    
    try:
        result = generate_question("telecollection", backend_conversation)
        print(f"✅ Result: {result}")
        print(f"Goal: {result.get('goal', 'N/A')}")
        print(f"Is Closing: {result.get('is_closing', False)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_format_compatibility()