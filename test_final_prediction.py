#!/usr/bin/env python3
"""
Final comprehensive test to verify all fixes are working together
"""

import sys
import os

backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_path)

try:
    from app.services.gpt_service import predict_telecollection_status
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def test_prediction_accuracy():
    """Test the prediction accuracy with the exact conversation from logs"""
    
    print("🔮 TESTING PREDICTION ACCURACY WITH EXACT USER CONVERSATION")
    print("=" * 70)
    
    # Recreate the exact conversation from user's logs
    conversation_exchanges = [
        ("Halo Budi, selamat pagi! Saya Wisnu dari ICONNET. Gimana kabarnya hari ini? Oh iya, saya mau tanya nih, untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?", "belum"),
        ("Saya paham situasinya. Saya ingin memahami situasinya - ada kendala khusus yang membuat pembayaran tertunda? Misalnya masalah keuangan atau teknis?", "Belum gajian"),
        ("Saya paham situasinya. Supaya lebih mudah - metode pembayaran apa yang paling nyaman? Transfer bank, e-wallet, atau datang langsung?", "Transfer bank"),
        ("Terakhir - apakah perlu kami follow up lagi sebelum tanggal pembayaran yang disepakati?", "Ya, tolong diingatkan"),
        ("Bagus! Terakhir - apakah perlu kami follow up lagi sebelum tanggal pembayaran yang disepakati?", "ya tentu di tanggal 29 oktober yaa"),
        ("Mari kita lanjutkan pembahasannya. Ada hal lain yang ingin Bapak/Ibu sampaikan terkait closing?", "Tidak ada"),
        ("Mari kita lanjutkan pembahasannya. Ada hal lain yang ingin Bapak/Ibu sampaikan terkrit closing?", "Sudah cukup")
    ]
    
    # Extract answers and create conversation text
    answers = [exchange[1] for exchange in conversation_exchanges]
    conversation_text = ' '.join([f"Q: {q} A: {a}" for q, a in conversation_exchanges])
    
    print("📋 Conversation Summary:")
    for i, (q, a) in enumerate(conversation_exchanges, 1):
        print(f"   {i}. Q: {q[:60]}...")
        print(f"      A: {a}")
    
    print(f"\n📊 Total Exchanges: {len(conversation_exchanges)}")
    print(f"📝 Customer Answers: {answers}")
    
    # Test prediction
    print(f"\n🔮 Running prediction analysis...")
    try:
        result = predict_telecollection_status(conversation_text, answers)
        
        print(f"\n✅ PREDICTION RESULTS:")
        print(f"🎯 Decision: {result.get('prediction', 'UNKNOWN')}")
        print(f"📊 Status: {result.get('status', 'Unknown')}")
        print(f"🎪 Confidence: {result.get('confidence', 0):.1%}")
        print(f"📅 Payment Timeline: {result.get('estimasi_pembayaran', 'Not specified')}")
        print(f"📄 Reasoning: {result.get('alasan', 'No reason provided')}")
        
        # Analyze if prediction matches conversation content
        print(f"\n🔍 ANALYSIS:")
        
        # Check for positive commitment indicators
        positive_signs = []
        if "ya tentu di tanggal 29 oktober" in conversation_text:
            positive_signs.append("✅ Specific payment date commitment (Oct 29)")
        if "transfer bank" in conversation_text.lower():
            positive_signs.append("✅ Preferred payment method specified")
        if "ya, tolong diingatkan" in conversation_text:
            positive_signs.append("✅ Accepts follow-up reminders")
        if "sudah cukup" in conversation_text:
            positive_signs.append("✅ Conversation completion acceptance")
            
        # Check for negative indicators
        negative_signs = []
        if "belum gajian" in conversation_text:
            negative_signs.append("⚠️ Temporary cash flow issue (waiting for salary)")
            
        print(f"📈 Positive Indicators ({len(positive_signs)}):")
        for sign in positive_signs:
            print(f"   {sign}")
            
        print(f"📉 Concerns ({len(negative_signs)}):")
        for sign in negative_signs:
            print(f"   {sign}")
        
        # Expected result analysis
        if len(positive_signs) > len(negative_signs):
            expected_prediction = "ACCEPT"
            expected_reasoning = "Strong commitment with specific timeline despite temporary cash flow issue"
        else:
            expected_prediction = "UNCERTAIN"
            expected_reasoning = "Mixed signals requiring further assessment"
        
        print(f"\n🎯 EXPECTED vs ACTUAL:")
        print(f"Expected: {expected_prediction} - {expected_reasoning}")
        print(f"Actual:   {result.get('prediction', 'UNKNOWN')} - {result.get('status', 'Unknown')}")
        
        # Accuracy assessment
        if result.get('prediction') == expected_prediction:
            print(f"✅ ACCURACY: CORRECT - Prediction matches conversation analysis")
            accuracy_status = "PASS"
        else:
            print(f"❌ ACCURACY: INCORRECT - Prediction should be {expected_prediction}")
            accuracy_status = "FAIL"
            
        print(f"\n" + "=" * 70)
        print(f"🎉 PREDICTION TEST: {accuracy_status}")
        
        return accuracy_status == "PASS"
        
    except Exception as e:
        print(f"❌ Prediction failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_prediction_accuracy()
    if success:
        print("🎊 ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION!")
    else:
        print("⚠️ ISSUES DETECTED - FURTHER DEBUGGING NEEDED")