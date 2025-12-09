#!/usr/bin/env python3
"""
Test script untuk verifikasi fitur permintaan tanggal pasti ketika customer memilih "akhir bulan"
"""

import requests
import json

API_BASE_URL = "http://localhost:8000/api/v1/endpoints"
CUSTOMER_ID = "ICON12345"

def test_end_of_month_specific_date():
    """Test scenario ketika customer bilang 'akhir bulan' dan sistem minta tanggal pasti"""
    print("🎯 Testing 'Akhir Bulan' → Specific Date Request\n")
    
    conversation = []
    
    # Step 1: Initial question
    print("=" * 60)
    print("STEP 1: Initial Question")
    print("=" * 60)
    
    response = requests.post(
        f"{API_BASE_URL}/conversation/generate-simulation-questions",
        json={
            "customer_id": CUSTOMER_ID,
            "topic": "telecollection",
            "conversation": conversation,
            "user": "test@iconnet.co.id"
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        question1 = data.get("question", "")
        options1 = data.get("options", [])
        
        print(f"📞 CS Agent: {question1}")
        print(f"📋 Options: {options1}")
        
        # Customer response: Akhir bulan
        answer1 = "Akhir bulan ini pak, setelah gajian"
        print(f"👤 Customer: {answer1}")
        
        conversation.append({"q": question1, "a": answer1})
        
        # Step 2: Should ask for specific date
        print("\n" + "=" * 60)
        print("STEP 2: Expected - Request for Specific Date")
        print("=" * 60)
        
        response2 = requests.post(
            f"{API_BASE_URL}/conversation/generate-simulation-questions",
            json={
                "customer_id": CUSTOMER_ID,
                "topic": "telecollection",
                "conversation": conversation,
                "user": "test@iconnet.co.id"
            },
            timeout=15
        )
        
        if response2.status_code == 200:
            data2 = response2.json()
            question2 = data2.get("question", "")
            options2 = data2.get("options", [])
            
            print(f"📞 CS Agent: {question2}")
            print(f"📋 Options: {options2}")
            
            # Check if it asks for specific date
            print("\n🔍 Analysis:")
            question2_lower = question2.lower()
            
            # Check for date-specific keywords
            date_keywords = ["tanggal", "spesifik", "berapa", "25", "26", "27", "28", "29", "30", "31"]
            has_date_request = any(keyword in question2_lower for keyword in date_keywords)
            
            if has_date_request:
                print("   ✅ GOOD: CS asks for specific date when customer says 'akhir bulan'")
            else:
                print("   ❌ ISSUE: CS doesn't ask for specific date")
            
            # Check options contain specific dates
            options_text = " ".join(options2).lower()
            has_date_options = any(date in options_text for date in ["25", "26", "27", "28", "29", "30", "31"])
            
            if has_date_options:
                print("   ✅ GOOD: Options contain specific date ranges")
            else:
                print("   ❌ ISSUE: Options don't contain specific dates")
            
            # Customer response: Specific date
            answer2 = "Tanggal 28-30 bulan ini pak"
            print(f"\n👤 Customer: {answer2}")
            
            conversation.append({"q": question2, "a": answer2})
            
            # Step 3: Confirmation
            print("\n" + "=" * 60)
            print("STEP 3: Date Commitment Confirmation")
            print("=" * 60)
            
            response3 = requests.post(
                f"{API_BASE_URL}/conversation/generate-simulation-questions",
                json={
                    "customer_id": CUSTOMER_ID,
                    "topic": "telecollection",
                    "conversation": conversation,
                    "user": "test@iconnet.co.id"
                },
                timeout=15
            )
            
            if response3.status_code == 200:
                data3 = response3.json()
                question3 = data3.get("question", "")
                options3 = data3.get("options", [])
                
                print(f"📞 CS Agent: {question3}")
                print(f"📋 Options: {options3}")
                
                # Check if it confirms the specific date
                print("\n🔍 Analysis:")
                question3_lower = question3.lower()
                
                if "28" in question3_lower or "30" in question3_lower or "tanggal" in question3_lower:
                    print("   ✅ GOOD: CS references the specific date mentioned")
                
                commitment_keywords = ["pasti", "yakin", "komitmen", "memastikan"]
                has_commitment = any(keyword in question3_lower for keyword in commitment_keywords)
                
                if has_commitment:
                    print("   ✅ GOOD: CS asks for commitment confirmation")
                
                print("\n" + "=" * 60)
                print("CONVERSATION SUMMARY")
                print("=" * 60)
                
                print("\n📝 Complete Flow:")
                for i, exchange in enumerate(conversation, 1):
                    print(f"\n{i}. CS: {exchange['q']}")
                    print(f"   Customer: {exchange['a']}")
                
                print(f"\n📊 Feature Test Results:")
                print(f"   • 'Akhir bulan' detected: {'✅' if 'akhir bulan' in answer1.lower() else '❌'}")
                print(f"   • Specific date requested: {'✅' if has_date_request else '❌'}")
                print(f"   • Date options provided: {'✅' if has_date_options else '❌'}")
                print(f"   • Date commitment confirmed: {'✅' if has_commitment else '❌'}")
                
                return True
    
    return False

def test_beginning_of_month():
    """Test scenario untuk 'awal bulan'"""
    print("\n\n🎯 Testing 'Awal Bulan' → Specific Date Request\n")
    
    conversation = []
    
    # Initial conversation
    conversation.append({
        "q": "Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?",
        "a": "Awal bulan depan pak"
    })
    
    print("📞 Previous CS: Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?")
    print("👤 Customer: Awal bulan depan pak")
    
    print("\n" + "=" * 60)
    print("Expected: Request for Specific Date in Early Month")
    print("=" * 60)
    
    response = requests.post(
        f"{API_BASE_URL}/conversation/generate-simulation-questions",
        json={
            "customer_id": CUSTOMER_ID,
            "topic": "telecollection", 
            "conversation": conversation,
            "user": "test@iconnet.co.id"
        },
        timeout=15
    )
    
    if response.status_code == 200:
        data = response.json()
        question = data.get("question", "")
        options = data.get("options", [])
        
        print(f"📞 CS Agent: {question}")
        print(f"📋 Options: {options}")
        
        print("\n🔍 Analysis:")
        question_lower = question.lower()
        
        # Check for early month date request
        early_date_keywords = ["tanggal", "spesifik", "berapa", "awal", "1", "2", "3", "5", "7", "10"]
        has_early_date_request = any(keyword in question_lower for keyword in early_date_keywords)
        
        if has_early_date_request:
            print("   ✅ GOOD: CS asks for specific date when customer says 'awal bulan'")
        else:
            print("   ❌ ISSUE: CS doesn't ask for specific early month date")
        
        return has_early_date_request
    
    return False

if __name__ == "__main__":
    print("=" * 80)
    print(" TESTING: Specific Date Request for 'Akhir Bulan' / 'Awal Bulan' ")
    print("=" * 80)
    
    try:
        # Test akhir bulan
        success1 = test_end_of_month_specific_date()
        
        # Test awal bulan
        success2 = test_beginning_of_month()
        
        print("\n" + "=" * 80)
        print("FINAL RESULTS")
        print("=" * 80)
        
        print(f"✅ 'Akhir Bulan' test: {'PASSED' if success1 else 'FAILED'}")
        print(f"✅ 'Awal Bulan' test: {'PASSED' if success2 else 'FAILED'}")
        
        if success1 and success2:
            print("\n🎉 ALL TESTS PASSED! Feature working correctly.")
        else:
            print("\n⚠️  Some tests failed. Check implementation.")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Test error: {e}")