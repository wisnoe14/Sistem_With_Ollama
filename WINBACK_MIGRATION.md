# Winback Service Migration Documentation

## Overview
This document describes the migration of winback prediction logic from the monolithic `gpt_service.py` to the dedicated `winback_services.py` file.

## Migration Date
**Date:** December 2024

## What Was Migrated

### Full Implementation
The complete `predict_winback_outcome()` function (~230 lines) has been migrated to `winback_services.py` as `predict_outcome()`.

### Key Features Migrated
1. **Interest Analysis**
   - Detects interest indicators: "tertarik", "mau", "boleh", "iya", "bagus", "menarik", "coba"
   - Calculates interest_score based on confidence levels

2. **Commitment Detection**
   - Tracks commitment keywords: "akan", "mau coba", "daftar", "aktivasi", "berminat"
   - Timeline detection: "hari ini", "besok", "seminggu", "jam", "nanti", "segera"
   - Calculates commitment_score

3. **Objection Handling**
   - Detects objections: "tidak tertarik", "gak mau", "nggak bisa", "provider lain"
   - Strong rejections: "pindah rumah", "tidak butuh internet", "sudah pakai provider lain"
   - Counts objections for scoring

4. **Price Sensitivity Analysis**
   - Tracks price-related mentions
   - Higher weight for "mahal" keyword
   - Contributes to final scoring

5. **Equipment Status Tracking**
   - Separates equipment responses from payment indicators
   - Tracks: "sudah dikembalikan", "hilang", "rusak", "masih ada", "kondisi"

6. **Promo Discussion Detection**
   - Detects promo-related keywords in conversation
   - Tracks "promo", "gratis", "bayar 1 bulan gratis 1 bulan"
   - Flags promo_discussed in analysis

7. **Answer Interpretations**
   - Detailed interpretation of each answer
   - Categorizes by type: commitment, timeline, objection, interest, price, promo, equipment
   - Includes sentiment analysis and confidence scores

8. **Decision Logic**
   - Multi-factor scoring algorithm
   - Five decision categories:
     - "BERHASIL REAKTIVASI" - Strong commitment detected
     - "TERTARIK REAKTIVASI" - Interest with commitment
     - "KEMUNGKINAN TERTARIK" - Interest with minimal objections
     - "TIDAK TERTARIK" - Strong rejection or high objections
     - "PERLU FOLLOW-UP" - Uncertain/neutral responses

9. **Risk Level Integration**
   - Automatic risk level computation
   - Returns: risk_level, risk_label, risk_color

10. **Ollama Integration**
    - Uses `generate_reason_with_ollama()` for natural language reasons
    - Includes analysis_data for context-aware generation

## File Changes

### `backend/app/services/winback_services.py`
**Before:**
```python
def predict_outcome(conversation_history: List[Dict]) -> Dict:
    """Predict winback outcome based on conversation history."""
    return _core.predict_winback_outcome(conversation_history)
```

**After:**
Full implementation with 230+ lines including:
- Empty conversation handling
- Interest, commitment, objection analysis
- Price sensitivity and cooperation tracking
- Equipment and promo detection
- Answer interpretations
- Multi-factor scoring
- Decision logic with strong rejection checks
- Risk level computation
- Ollama-based reason generation

### `backend/app/services/gpt_service.py`
**Before:**
```python
def predict_winback_outcome(conversation_history: List[Dict]) -> Dict:
    """PREDICTION: Prediksi hasil winback (reaktivasi customer)"""
    # ... 230+ lines of implementation
```

**After:**
```python
def predict_winback_outcome(conversation_history: List[Dict]) -> Dict:
    """
    DEPRECATED: Use winback_services.predict_outcome() instead.
    This function is kept for backward compatibility only.
    
    Redirects to the dedicated winback service implementation.
    """
    from .winback_services import predict_outcome
    return predict_outcome(conversation_history)
```

## Dependencies

The migrated code uses the following from `_core` (gpt_service):
- `get_current_date_info()` - Date formatting
- `analyze_sentiment_and_intent()` - Sentiment analysis
- `generate_reason_with_ollama()` - AI-based reason generation
- `compute_risk_level()` - Risk indicator calculation

## Backward Compatibility

✅ **Fully Maintained**
- Old imports still work: `from app.services.gpt_service import predict_winback_outcome`
- Function signature unchanged
- Return structure identical
- No breaking changes to API endpoints

## Testing

Run the test suite:
```bash
python test_winback_migration.py
```

Test coverage includes:
1. ✅ Import verification
2. ✅ Prediction functionality
3. ✅ Backward compatibility
4. ✅ Promo detection
5. ✅ Objection handling

## Benefits

1. **Modularity**
   - Winback logic isolated in dedicated file
   - Easier to maintain and update
   - Clear separation of concerns

2. **Code Organization**
   - Related functions grouped together
   - Better file structure
   - Reduced file size of gpt_service.py

3. **Maintainability**
   - Easier to find winback-specific code
   - Changes don't affect other modes
   - Better for team collaboration

4. **Testing**
   - Isolated testing possible
   - Mock dependencies more easily
   - Better test coverage

## Migration Pattern

This migration follows the same pattern as telecollection:

1. **Copy Implementation**
   - Full function code copied to dedicated service
   - Updated to use `_core.` prefix for shared utilities

2. **Create Redirect**
   - Old function becomes a simple redirect
   - Deprecation notice added
   - Backward compatibility maintained

3. **Test & Verify**
   - Test suite created
   - All functionality verified
   - No breaking changes

## Future Improvements

1. **Extract Shared Utilities**
   - Move common functions to a shared module
   - Reduce dependency on _core import

2. **Enhanced Testing**
   - Add more edge case tests
   - Integration tests with real Ollama
   - Performance benchmarks

3. **Documentation**
   - Add inline code comments
   - Create API documentation
   - Usage examples

## Related Migrations

- ✅ **Telecollection** - Completed (see TELECOLLECTION_MIGRATION.md)
- ✅ **Winback** - Completed (this document)
- 🔜 **Retention** - Pending

## Usage Examples

### Using New Service
```python
from app.services.winback_services import predict_outcome

conversation = [
    {"q": "Kenapa berhenti?", "a": "Sering gangguan"},
    {"q": "Kondisi perangkat?", "a": "Masih ada"},
    {"q": "Ada promo comeback", "a": "Tertarik"}
]

result = predict_outcome(conversation)
print(result['keputusan'])  # e.g., "TERTARIK REAKTIVASI"
```

### Using Old Import (Still Works)
```python
from app.services.gpt_service import predict_winback_outcome

result = predict_winback_outcome(conversation)  # Redirects to new service
```

## Verification Checklist

- [x] Full implementation migrated
- [x] All features preserved
- [x] Backward compatibility maintained
- [x] Test suite created
- [x] Documentation written
- [x] No breaking changes
- [x] Risk indicators included
- [x] Ollama integration working
- [x] Answer interpretations complete
- [x] Promo detection functional

## Notes

- The migration maintains 100% functional parity with the original
- All analysis features are preserved
- Risk level computation integrated
- Answer interpretations included
- Deprecation warning added for gradual transition
- No changes needed in endpoints or frontend

---

**Migration Status:** ✅ COMPLETE
**Backward Compatible:** ✅ YES
**Tests Passing:** ✅ YES
**Production Ready:** ✅ YES
