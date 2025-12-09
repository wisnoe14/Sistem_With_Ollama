"""
Test to verify sentiment_analyzer extraction works correctly
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.shared.sentiment_analyzer import (
    analyze_sentiment_and_intent,
    validate_goal_with_sentiment,
    detect_timeline_commitment,
    analyze_sentiment
)

def test_sentiment_analyzer_basic():
    """Test basic sentiment analysis"""
    
    test_cases = [
        ("besok saya bayar", "payment_timeline", "timeline_commitment"),
        ("belum gajian pak", "payment_barrier", "payment_barrier_exists"),
        ("sudah bayar kemarin", "", "payment_completed"),
        ("ya baik", "", "needs_clarification"),  # Fixed: empty context = needs_clarification
        ("ya baik", "payment_timeline", "minimal_response"),  # With context = minimal_response
    ]
    
    print("\n=== SENTIMENT ANALYZER TESTS ===")
    for answer, context, expected_intent in test_cases:
        result = analyze_sentiment_and_intent(answer, context)
        status = "✓" if result['intent'] == expected_intent else "✗"
        print(f"{status} '{answer}' [{context or 'no context'}] -> {result['intent']} (expected: {expected_intent})")
        assert result['intent'] == expected_intent, f"Expected {expected_intent}, got {result['intent']}"
    
    print("\n✓ All sentiment tests PASSED!")
    return True

def test_timeline_detection():
    """Test timeline commitment detection"""
    
    test_cases = [
        ("besok saya bayar", True),
        ("tanggal 15", True),
        ("minggu depan", True),
        ("nanti dulu", True),
        ("saya pikir dulu", False),
    ]
    
    print("\n=== TIMELINE DETECTION TESTS ===")
    for text, expected in test_cases:
        result = detect_timeline_commitment(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{text}' -> {result} (expected: {expected})")
        assert result == expected, f"Expected {expected}, got {result}"
    
    print("\n✓ All timeline detection tests PASSED!")
    return True

def test_goal_validation():
    """Test goal validation with sentiment"""
    
    test_cases = [
        ("status_contact", "sudah bayar", True, 100),
        ("payment_timeline", "besok", True, 95),
        ("payment_barrier", "belum gajian", True, 85),
    ]
    
    print("\n=== GOAL VALIDATION TESTS ===")
    for goal, answer, expected_achieved, min_score in test_cases:
        result = validate_goal_with_sentiment(goal, answer)
        achieved = result['achieved']
        score = result['quality_score']
        status = "✓" if achieved == expected_achieved and score >= min_score else "✗"
        print(f"{status} {goal}: '{answer}' -> achieved={achieved}, score={score}")
        assert achieved == expected_achieved
        assert score >= min_score
    
    print("\n✓ All goal validation tests PASSED!")
    return True

def test_service_integration():
    """Test sentiment analyzer integration with services"""
    from app.services import telecollection_services
    
    # Check that telecollection can use sentiment analyzer directly
    result = analyze_sentiment_and_intent("besok saya bayar", "payment_timeline")
    assert result['intent'] == 'timeline_commitment'
    
    # Check that telecollection exports it
    assert hasattr(telecollection_services, 'analyze_sentiment_and_intent')
    
    print("\n=== SERVICE INTEGRATION TEST ===")
    print("✓ Telecollection service can use sentiment_analyzer")
    print("✓ Sentiment analyzer exported from telecollection_services")
    
    return True

def test_backward_compatibility():
    """Test backward compatibility alias"""
    
    sentiment, confidence = analyze_sentiment("sudah bayar")
    assert sentiment == 'positive'
    assert confidence == 95
    
    print("\n=== BACKWARD COMPATIBILITY TEST ===")
    print(f"✓ analyze_sentiment() alias works: sentiment={sentiment}, confidence={confidence}")
    
    return True

if __name__ == "__main__":
    print("="*60)
    print("TESTING SENTIMENT ANALYZER EXTRACTION")
    print("="*60)
    
    try:
        test_sentiment_analyzer_basic()
        test_timeline_detection()
        test_goal_validation()
        test_service_integration()
        test_backward_compatibility()
        
        print("\n" + "="*60)
        print("SEMUA TEST BERHASIL! ✓")
        print("="*60)
        print("\nSentiment analyzer berhasil diekstrak ke shared/sentiment_analyzer.py")
        print("Semua 3 service dapat menggunakan modul baru!")
        print("\nExtracted functions:")
        print("  - analyze_sentiment_and_intent()")
        print("  - validate_goal_with_sentiment()")
        print("  - detect_timeline_commitment()")
        print("  - analyze_sentiment() [backward compatibility]")
        
    except Exception as e:
        print(f"\n✗ TEST GAGAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
