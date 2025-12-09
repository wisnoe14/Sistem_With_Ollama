#!/usr/bin/env python3
"""
Test specific telecollection scenarios for better reason generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.services.telecollection_services import predict_outcome as predict_telecollection_outcome

def test_telecollection_scenarios():
    """Test various telecollection scenarios"""
    
    # Test Case 1: Clear commitment with date
    print("="*60)
    print("TEST CASE 1: Clear Commitment with Specific Date")
    print("="*60)
    
    conversation_1 = [
        {"a": "Bisa Dihubungi", "goal": "status_contact"},
        {"a": "Belum bayar, tapi besok akan transfer", "goal": "payment_status"}, 
        {"a": "Besok sore sekitar jam 3", "goal": "payment_timeline"},
        {"a": "Lewat mobile banking", "goal": "payment_method"},
        {"a": "Pasti akan bayar besok", "goal": "commitment_confirm"}
    ]
    
    result_1 = predict_telecollection_outcome(conversation_1)
    print(f"Keputusan: {result_1.get('keputusan')}")
    print(f"Probability: {result_1.get('probability')}%") 
    print(f"Alasan: {result_1.get('alasan')}")
    
    # Test Case 2: Multiple barriers
    print("\n" + "="*60)
    print("TEST CASE 2: Multiple Serious Barriers")
    print("="*60)
    
    conversation_2 = [
        {"a": "Bisa Dihubungi", "goal": "status_contact"},
        {"a": "Susah bayar, lagi krisis", "goal": "payment_status"},
        {"a": "Usaha tutup", "goal": "payment_barrier"},
        {"a": "Gak ada uang", "goal": "financial_capability"}, 
        {"a": "Gak tau kapan bisa bayar", "goal": "payment_timeline"}
    ]
    
    result_2 = predict_telecollection_outcome(conversation_2)
    print(f"Keputusan: {result_2.get('keputusan')}")
    print(f"Probability: {result_2.get('probability')}%")
    print(f"Alasan: {result_2.get('alasan')}")
    
    # Test Case 3: Cooperative but uncertain
    print("\n" + "="*60)
    print("TEST CASE 3: Cooperative but Uncertain Timeline")
    print("="*60)
    
    conversation_3 = [
        {"a": "Bisa Dihubungi", "goal": "status_contact"},
        {"a": "Belum bisa bayar sekarang", "goal": "payment_status"},
        {"a": "Tunggu gaji masuk dulu", "goal": "payment_barrier"},
        {"a": "Biasanya tanggal 25", "goal": "payment_timeline"},
        {"a": "Iya, nanti akan bayar", "goal": "commitment_confirm"}
    ]
    
    result_3 = predict_telecollection_outcome(conversation_3)
    print(f"Keputusan: {result_3.get('keputusan')}")
    print(f"Probability: {result_3.get('probability')}%")
    print(f"Alasan: {result_3.get('alasan')}")

    # Test Case 4: Payment completed
    print("\n" + "="*60)
    print("TEST CASE 4: Payment Already Completed")
    print("="*60)
    
    conversation_4 = [
        {"a": "Bisa Dihubungi", "goal": "status_contact"},
        {"a": "Sudah bayar kemarin lewat ATM", "goal": "payment_status"},
        {"a": "Lewat BCA", "goal": "payment_method"},
        {"a": "Jam 8 malam kemarin", "goal": "payment_timeline"}
    ]
    
    result_4 = predict_telecollection_outcome(conversation_4)
    print(f"Keputusan: {result_4.get('keputusan')}")
    print(f"Probability: {result_4.get('probability')}%")
    print(f"Alasan: {result_4.get('alasan')}")

if __name__ == "__main__":
    test_telecollection_scenarios()