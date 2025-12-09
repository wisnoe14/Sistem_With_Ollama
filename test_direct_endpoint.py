#!/usr/bin/env python3
"""
Test Conversation Endpoint Directly
Test function generate_simulation_questions langsung tanpa server
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import function langsung
from app.api.v1.endpoints.conversation import generate_simulation_questions
from app.models.conversation import GenerateSimulationRequest
from pydantic import BaseModel
from typing import List, Dict

class ConversationItem(BaseModel):
    q: str
    a: str

def test_conversation_endpoint():
    """Test generate_simulation_questions function directly"""
    print("=" * 60)
    print("🔧 TESTING CONVERSATION ENDPOINT DIRECTLY")
    print("=" * 60)
    
    # Test 1: Customer says "Selesai" 
    print("\n📋 TEST 1: Customer says 'Selesai'")
    
    conversation_data = [
        ConversationItem(q="Halo, bagaimana pembayaran bulan ini?", a="Belum bisa bayar"),
        ConversationItem(q="Kapan bisa bayar?", a="Minggu depan"),
        ConversationItem(q="Baik, ada yang lain?", a="Selesai")
    ]
    
    request = GenerateSimulationRequest(
        topic="telecollection",
        customer_id="ICON12345", 
        user="test@iconnet.com",
        conversation=conversation_data
    )
    
    try:
        # Mock database dependency
        class MockDB:
            def query(self, model):
                class MockQuery:
                    def filter(self, condition):
                        return self
                    def first(self):
                        return None
                return MockQuery()
        
        result = generate_simulation_questions(request, MockDB())
        
        print(f"✅ Is Closing: {result.get('is_closing', False)}")
        print(f"🔚 Closing Reason: {result.get('closing_reason', 'N/A')}")
        print(f"🔍 Detected Keyword: {result.get('detected_keyword', 'N/A')}")
        print(f"❓ Question: {result.get('question', 'N/A')[:100]}...")
        
        if result.get('is_closing'):
            print(f"\n🎉 SUCCESS: Customer 'Selesai' detected and conversation closed!")
        else:
            print(f"\n❌ FAILED: Customer 'Selesai' not detected")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: Normal conversation
    print(f"\n{'='*60}")
    print("📋 TEST 2: Normal conversation (should continue)")
    
    conversation_data_2 = [
        ConversationItem(q="Bagaimana pembayaran?", a="Lagi nyari uang dulu")
    ]
    
    request_2 = GenerateSimulationRequest(
        topic="telecollection",
        customer_id="ICON12345",
        user="test@iconnet.com", 
        conversation=conversation_data_2
    )
    
    try:
        result_2 = generate_simulation_questions(request_2, MockDB())
        
        print(f"✅ Is Closing: {result_2.get('is_closing', False)}")
        print(f"❓ Should Continue: {not result_2.get('is_closing', False)}")
        
        if not result_2.get('is_closing'):
            print(f"\n🎉 SUCCESS: Normal conversation continues as expected!")
        else:
            print(f"\n❌ FAILED: Conversation closed unexpectedly")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    test_conversation_endpoint()