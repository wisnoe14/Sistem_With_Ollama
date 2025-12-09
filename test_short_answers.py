import sys
sys.path.append('backend')

from app.services.gpt_service import analyze_sentiment_and_intent, validate_goal_with_sentiment

print("=== TESTING SHORT ANSWER ACCEPTANCE ===")

# Test short answers with different goals
test_cases = [
    ("ya", "payment_barrier", "Should accept 'ya' as barrier acknowledgment"),
    ("hmm", "payment_timeline", "Should accept 'hmm' as minimal timeline response"),
    ("oke", "payment_barrier", "Should accept 'oke' as barrier response"),
    ("baik", "payment_timeline", "Should accept 'baik' as timeline response"),
    ("siap", "payment_barrier", "Should accept 'siap' as barrier response"),
]

print("\nTesting short answer sentiment analysis:")
for answer, goal, description in test_cases:
    sentiment = analyze_sentiment_and_intent(answer, goal)
    validation = validate_goal_with_sentiment(goal, answer)
    
    print(f"\nAnswer: '{answer}' | Goal: {goal}")
    print(f"  Sentiment: {sentiment['sentiment']} | Intent: {sentiment['intent']} | Confidence: {sentiment['confidence']}%")
    print(f"  Goal achieved: {validation['achieved']} | Score: {validation['quality_score']}")
    print(f"  Expected: {description}")

print("\n" + "="*50)
print("SOLUTION: Need to make 'minimal_response' trigger goal achievement")