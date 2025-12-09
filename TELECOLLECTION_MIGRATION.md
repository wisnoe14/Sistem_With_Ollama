# Telecollection Migration Guide

## 🎯 Tujuan Migrasi
Memindahkan logika telecollection dari monolithic `gpt_service.py` ke dedicated service file `telecollection_services.py` untuk meningkatkan maintainability dan modularitas.

## ✅ Yang Sudah Selesai

### 1. **Fungsi Prediction Lengkap Sudah Dimigrasikan**
   - `predict_outcome()` di `telecollection_services.py` sekarang berisi full implementation
   - Sebelumnya hanya redirect ke `_core.predict_telecollection_outcome()`
   - Sekarang standalone dengan semua logika scoring, analysis, dan prediction

### 2. **Backward Compatibility Dijaga**
   - `gpt_service.py` masih bisa digunakan (dengan deprecation warning)
   - `predict_telecollection_outcome()` di gpt_service redirect ke service baru
   - Existing code tidak akan break

### 3. **File Organization**
   - ✅ `backend/app/services/telecollection_services.py` - Main service file
   - ⚠️ `backend/app/services/gpt_service.py` - Deprecated, redirect saja

## 📊 Struktur telecollection_services.py

```
telecollection_services.py
├── Question Generation
│   ├── generate_question() - Rule-based question flow
│   ├── Helper functions (_ask_*, _closing_message, etc)
│   └── NLP helpers (_norm, _has, _is_yes_owner, etc)
│
├── Prediction Logic
│   ├── predict_outcome() - FULL IMPLEMENTATION (migrated)
│   │   ├── Analysis loop (sentiment, barriers, timeline)
│   │   ├── Scoring system (commitment, barriers, cooperation)
│   │   ├── Decision logic (SUDAH BAYAR, AKAN BAYAR, etc)
│   │   └── Risk computation
│   └── Helper: analyze_sentiment_and_intent (from _core)
│
└── Goal Management
    ├── check_goals() - Check conversation goals
    └── determine_next_goal() - Determine next step
```

## 🔄 Migration Steps Completed

### Step 1: Copy Full Implementation ✅
- Copied `predict_telecollection_outcome` dari gpt_service.py
- Renamed menjadi `predict_outcome` di telecollection_services.py
- Updated semua calls ke _core functions (get_current_date_info, compute_risk_level, etc)

### Step 2: Update gpt_service.py ✅
- Replaced full implementation dengan redirect function
- Added deprecation notice
- Kept function signature sama untuk compatibility

### Step 3: Verify Dependencies ✅
- Semua shared utilities masih dari _core (temporary)
- analyze_sentiment_and_intent
- parse_time_expressions_to_date
- get_current_date_info
- generate_reason_with_ollama (dengan natural barrier format)
- compute_risk_level
- _extract_barrier_essence

## 📝 Usage Examples

### ✅ **Recommended (New Way)**
```python
from app.services.telecollection_services import predict_outcome

result = predict_outcome(conversation_history)
```

### ⚠️ **Still Works (Old Way - Deprecated)**
```python
from app.services.gpt_service import predict_telecollection_outcome

result = predict_telecollection_outcome(conversation_history)
# Will redirect to telecollection_services.predict_outcome
```

### 🎯 **In API Endpoints**
```python
from app.services import telecollection_services as tc_services

# Generate question
question = tc_services.generate_question(conversation)

# Predict outcome
prediction = tc_services.predict_outcome(conversation)
```

## 🧪 Testing

### Test Script: `test_telecollection_migration.py`

```bash
python test_telecollection_migration.py
```

**Tests:**
1. ✅ Import dari telecollection_services
2. ✅ Import dari gpt_service (redirect)
3. ✅ Basic functionality (empty conversation)
4. ✅ Sample conversation prediction
5. ✅ Backward compatibility verification

## 🔧 Technical Details

### Dependencies (Currently from _core)
These will be migrated to shared_utils in future:
- `analyze_sentiment_and_intent()` - Sentiment analysis
- `parse_time_expressions_to_date()` - Date parsing
- `get_current_date_info()` - Current date utilities
- `generate_reason_with_ollama()` - Natural language reason generation
- `compute_risk_level()` - Risk indicator computation
- `_extract_barrier_essence()` - Natural barrier formatting
- `check_conversation_goals()` - Goal checking
- `determine_next_goal()` - Next goal determination

### Features Migrated
- ✅ Payment completion detection
- ✅ Timeline commitment analysis
- ✅ Barrier identification and scoring
- ✅ Cooperation level measurement
- ✅ Sentiment pattern analysis
- ✅ Multi-stage decision logic
- ✅ Risk computation integration
- ✅ Natural language reason generation dengan barrier essence

## 📦 Endpoints Using This Service

### `/api/v1/conversation/predict`
```python
from app.services import telecollection_services as tc_services

if topic == "telecollection":
    prediction = tc_services.predict_outcome(conversation)
```

### `/api/v1/conversation/cs-chatbot/next-question`
```python
from app.services import telecollection_services as tc_services

if topic == "telecollection":
    question = tc_services.generate_question(conversation)
```

## 🚀 Next Steps

### Future Migrations (Not Yet Done)
1. **Shared Utilities Extraction**
   - Move common functions to `shared_utils.py`
   - Remove dependency on _core

2. **Winback & Retention Migration**
   - Apply same pattern to winback_services.py
   - Apply same pattern to retention_services.py

3. **Complete Removal of gpt_service.py**
   - After all modes migrated
   - Only keep truly shared utilities

## ⚠️ Breaking Changes

### None!
Migration is fully backward compatible. Old code will continue to work with deprecation warnings.

## 📚 Documentation

- Main service: `backend/app/services/telecollection_services.py`
- Test script: `test_telecollection_migration.py`
- Natural barrier format: `NATURAL_BARRIER_FORMAT.md`
- This guide: `TELECOLLECTION_MIGRATION.md`

## ✅ Checklist

- [x] Copy predict_telecollection_outcome to telecollection_services.py
- [x] Update to use _core imports
- [x] Create redirect in gpt_service.py
- [x] Add deprecation warning
- [x] Create test script
- [x] Test backward compatibility
- [x] Verify API endpoints still work
- [x] Document migration
- [ ] Migrate shared utilities (future)
- [ ] Migrate winback (future)
- [ ] Migrate retention (future)

---

## 🎉 Summary

Migrasi telecollection berhasil dilakukan dengan:
- **Zero breaking changes** - Semua existing code tetap works
- **Better organization** - Logic terpisah per mode
- **Full feature parity** - Tidak ada features yang hilang
- **Natural barrier format** - Improved UX dengan kendala yang natural
- **Future-ready** - Mudah untuk migrasi mode lainnya

Migration successful! ✅
