# Shared Utilities Module

**Location:** `backend/app/services/shared/`  
**Purpose:** Reusable utility functions for telecollection, winback, and retention services

---

## 📋 Overview

This module contains **5 shared utility modules** extracted from the monolithic `gpt_service.py` to follow the **Single Responsibility Principle** and improve code maintainability.

**Benefits:**
- ✅ **DRY (Don't Repeat Yourself)** - Share common logic across services
- ✅ **Testability** - Each module has independent unit tests
- ✅ **Maintainability** - Changes isolated to single modules
- ✅ **Scalability** - Easy to add new services or utilities

---

## 📦 Available Modules

### 1. `risk_calculator.py`
**Purpose:** Calculate customer churn risk indicators

**Main Function:**
```python
from .shared.risk_calculator import compute_risk_level

risk = compute_risk_level(
    conversation_history=[{"a": "Saya tidak bisa bayar"}],
    mode="telecollection",
    prediction={"keputusan": "TIDAK AKAN BAYAR"}
)
# Returns: {'risk_level': 'high', 'risk_label': 'Berisiko Tinggi', 'risk_color': '#dc2626', 'signals': [...]}
```

**Features:**
- Keyword-based heuristic analysis
- Risk scoring with labels (Aman, Waspada, Bahaya)
- Color coding for UI display
- Signal detection for actionable insights

**Tests:** `test_risk_calculator_extraction.py` (4/4 passing)

---

### 2. `sentiment_analyzer.py`
**Purpose:** Analyze customer sentiment and intent from responses

**Main Functions:**
```python
from .shared.sentiment_analyzer import (
    analyze_sentiment_and_intent,
    validate_goal_with_sentiment,
    detect_timeline_commitment
)

# 1. Analyze sentiment and intent
sentiment = analyze_sentiment_and_intent(
    answer="Besok pagi saya bayar",
    goal_context="payment_timeline"
)
# Returns: {'sentiment': 'positive', 'intent': 'timeline_commitment', 'confidence': 90, 'action': 'accept_timeline'}

# 2. Validate goal achievement
validation = validate_goal_with_sentiment(
    goal="payment_timeline",
    answer="Besok saya bayar"
)
# Returns: {'achieved': True, 'quality_score': 85, 'payment_complete': False, ...}

# 3. Detect timeline commitment
timeline = detect_timeline_commitment("Besok pagi saya transfer")
# Returns: True/False
```

**Features:**
- Context-aware sentiment detection (positive, negative, neutral, tentative)
- Intent classification (commitment, barrier, needs_clarification, etc.)
- Timeline parsing with regex patterns
- Payment barrier identification
- Support for all conversation modes

**Tests:** `test_sentiment_analyzer_extraction.py` (13/13 passing)

---

### 3. `date_utils.py`
**Purpose:** Indonesian date formatting and parsing utilities

**Main Functions:**
```python
from .shared.date_utils import (
    format_date_indonesian,
    get_current_date_info,
    parse_time_expressions_to_date,
    parse_relative_date
)

# 1. Get current date in various formats
date_info = get_current_date_info()
# Returns: {'tanggal_lengkap': 'Senin, 11 November 2025', 'tanggal_pendek': '11 Nov 2025', ...}

# 2. Parse Indonesian time expressions
timeline = parse_time_expressions_to_date("Saya akan bayar besok pagi")
# Returns: {'original_text': '...', 'detected_timeframe': 'besok', 'target_date': datetime(...), ...}

# 3. Format dates in Indonesian
formatted = format_date_indonesian(datetime(2025, 11, 11))
# Returns: "11 November 2025"

# 4. Parse relative dates
date = parse_relative_date("besok", from_date=datetime.now())
# Returns: datetime object for tomorrow
```

**Features:**
- Indonesian month names (Januari, Februari, etc.)
- Relative date parsing (besok, lusa, minggu depan)
- Timeline expression detection with regex
- Number patterns (3 hari, 2 minggu, 1 bulan)
- ISO 8601 formatting

**Tests:** `test_date_utils_extraction.py` (15/15 passing)

---

### 4. `data_persistence.py`
**Purpose:** Save and export conversation data

**Main Functions:**
```python
from .shared.data_persistence import (
    save_conversation_to_excel,
    update_conversation_context
)

# 1. Save conversation to Excel
filepath = save_conversation_to_excel(
    customer_id="CUST123",
    mode="telecollection",
    conversation=[{"question": "Kapan bayar?", "answer": "Besok", ...}],
    prediction={"keputusan": "AKAN BAYAR", "confidence": "TINGGI"}
)
# Returns: 'conversations/conversation_CUST123_telecollection_20251111_100000.xlsx'

# 2. Update conversation context (legacy compatibility)
# Note: This function signature may vary - check implementation
```

**Features:**
- Excel export with pandas DataFrame
- Automatic directory creation
- Timestamp-based unique filenames
- Prediction results included in export
- Support for all conversation modes

**Tests:** `test_data_persistence_extraction.py` (12/12 passing)

---

### 5. `ollama_client.py`
**Purpose:** LLM API integration for Ollama (Llama3)

**Main Functions:**
```python
from .shared.ollama_client import (
    check_ollama_models,
    warmup_ollama_model,
    ask_llama3_chat,
    generate_reason_with_ollama,
    get_ollama_performance_report,
    OLLAMA_STATS
)

# 1. Check if Ollama models are available
available = check_ollama_models()
# Returns: True/False

# 2. Warmup model to memory
warmup_ollama_model()

# 3. Generate prediction reason/explanation
reason = generate_reason_with_ollama(
    conversation_history=[{"q": "Kapan bayar?", "a": "Besok pagi"}],
    mode="telecollection",
    keputusan="AKAN BAYAR",
    analysis_data={
        "timeline_commitments": True,
        "barriers": False,
        "cooperation_level": 80
    }
)
# Returns: "Customer menunjukkan komitmen kuat untuk membayar besok pagi..."

# 4. Get performance metrics
report = get_ollama_performance_report()
# Returns: {'total_calls': 10, 'success_rate': '90%', 'average_response_time': '2.5s', ...}

# 5. Access statistics
print(OLLAMA_STATS)
# {'total_calls': 10, 'successful_calls': 9, 'failed_calls': 1, ...}
```

**Features:**
- Automatic model availability checking with caching
- Smart warmup with 30-minute keep-alive
- Timeout handling and error recovery
- Performance statistics tracking
- Fallback mechanisms for reliability
- Support for telecollection, winback, retention modes
- Configurable temperature, token limits, context size

**Tests:** `test_ollama_client_extraction.py` (import test passing)

---

## 🔧 Usage Guidelines

### Import Pattern
Always import from `.shared.module_name`:

```python
# ✅ CORRECT - Direct import from shared module
from .shared.risk_calculator import compute_risk_level
from .shared.sentiment_analyzer import analyze_sentiment_and_intent
from .shared.date_utils import get_current_date_info

# ❌ WRONG - Don't import from gpt_service (legacy)
from . import gpt_service as _core
risk = _core.compute_risk_level(...)  # Don't do this!
```

### Using Multiple Modules Together
Example: Telecollection prediction workflow

```python
from .shared.risk_calculator import compute_risk_level
from .shared.sentiment_analyzer import analyze_sentiment_and_intent
from .shared.date_utils import get_current_date_info, parse_time_expressions_to_date
from .shared.ollama_client import generate_reason_with_ollama

def predict_payment(conversation_history):
    # Get current date context
    date_info = get_current_date_info()
    
    # Analyze latest customer answer
    latest_answer = conversation_history[-1].get('a', '')
    
    # Parse timeline if mentioned
    timeline = parse_time_expressions_to_date(latest_answer)
    
    # Analyze sentiment and intent
    sentiment = analyze_sentiment_and_intent(
        latest_answer,
        goal_context="payment_timeline"
    )
    
    # Calculate risk level
    risk = compute_risk_level(
        conversation_history,
        mode="telecollection"
    )
    
    # Generate explanation with Ollama
    reason = generate_reason_with_ollama(
        conversation_history=conversation_history,
        mode="telecollection",
        keputusan="AKAN BAYAR" if sentiment['intent'] == 'timeline_commitment' else "TIDAK AKAN BAYAR",
        analysis_data={
            "timeline_commitments": bool(timeline),
            "barriers": risk['risk_level'] == 'high',
            "cooperation_level": sentiment.get('confidence', 0)
        }
    )
    
    return {
        "keputusan": "AKAN BAYAR" if sentiment['sentiment'] == 'positive' else "TIDAK AKAN BAYAR",
        "timeline": timeline,
        "risk": risk,
        "reason": reason
    }
```

---

## 🧪 Testing

Each module has comprehensive unit tests in the root directory:

```bash
# Run individual module tests
python test_risk_calculator_extraction.py        # 4 tests
python test_sentiment_analyzer_extraction.py     # 13 tests
python test_date_utils_extraction.py            # 15 tests
python test_data_persistence_extraction.py      # 12 tests
python test_ollama_client_extraction.py         # Basic import test

# Run integration tests
python test_phase2_integration.py               # 12 tests
```

**Total test coverage:** 72 tests (44 unit + 12 integration + 16 service)

---

## 📊 Module Dependencies

```
telecollection_services.py
├── risk_calculator (compute_risk_level)
├── sentiment_analyzer (analyze_sentiment_and_intent)
├── date_utils (get_current_date_info, parse_time_expressions_to_date)
└── ollama_client (generate_reason_with_ollama)

winback_services.py
├── risk_calculator (compute_risk_level)
├── sentiment_analyzer (analyze_sentiment_and_intent)
├── date_utils (get_current_date_info)
└── ollama_client (generate_reason_with_ollama)

retention_services.py
├── risk_calculator (compute_risk_level)
├── sentiment_analyzer (analyze_sentiment_and_intent)
└── date_utils (get_current_date_info)
```

**No circular dependencies** ✅ - All modules are independent

---

## 🔄 Migration from Legacy Code

If you're updating old code that uses `gpt_service._core`:

**Before (Legacy):**
```python
from . import gpt_service as _core

risk = _core.compute_risk_level(answer)
sentiment = _core.analyze_sentiment_and_intent(answer, context)
date_info = _core.get_current_date_info()
```

**After (Modern):**
```python
from .shared.risk_calculator import compute_risk_level
from .shared.sentiment_analyzer import analyze_sentiment_and_intent
from .shared.date_utils import get_current_date_info

risk = compute_risk_level([{"a": answer}], mode="telecollection")
sentiment = analyze_sentiment_and_intent(answer, goal_context=context)
date_info = get_current_date_info()
```

**Note:** Check function signatures - some parameters have changed for better clarity!

---

## 📚 Documentation

- **Phase 2 Progress:** `PHASE_2_PROGRESS.md`
- **Completion Summary:** `PHASE_2_COMPLETION_SUMMARY.md`
- **Verification Report:** `POST_PHASE2_VERIFICATION.md`

---

## 🚀 Future Enhancements

Potential additions to shared modules:

1. **validation_utils.py** - Input validation helpers
2. **logging_utils.py** - Structured logging for conversation tracking
3. **metrics_utils.py** - Performance and quality metrics
4. **cache_utils.py** - Caching layer for expensive operations
5. **notification_utils.py** - Alert/notification helpers

---

## 👥 Contributing

When adding new shared utilities:

1. **Create new module** in `backend/app/services/shared/`
2. **Add exports** to `__init__.py`
3. **Write comprehensive tests** in root directory
4. **Update this README** with usage examples
5. **Run all tests** to ensure no regressions

---

## ✅ Quality Checklist

Before committing changes to shared modules:

- [ ] Function has clear docstring with examples
- [ ] Type hints for all parameters and return values
- [ ] Error handling with graceful fallbacks
- [ ] Unit tests cover happy path and edge cases
- [ ] No circular dependencies introduced
- [ ] Existing services still work (run integration tests)
- [ ] README updated with new functionality

---

# Shared Utilities Modules

This folder contains all shared utility modules for the ICONNET Percakapan System. These modules are designed for reuse across telecollection, winback, and retention services.

## 📦 Modules
- `risk_calculator.py` — Churn risk analysis
- `sentiment_analyzer.py` — Sentiment and intent detection
- `date_utils.py` — Indonesian date parsing and formatting
- `data_persistence.py` — Conversation export and context update
- `ollama_client.py` — LLM API integration and performance tracking

## 🛠 Usage Example
Import shared functions directly in your service:
```python
from .shared.risk_calculator import compute_risk_level
from .shared.sentiment_analyzer import analyze_sentiment_and_intent
from .shared.date_utils import get_current_date_info
from .shared.ollama_client import generate_reason_with_ollama
```

## 🧩 Architecture Principles
- **Single Responsibility:** Each module has one clear domain
- **Explicit Exports:** Only public APIs exposed via `__init__.py`
- **No Circular Dependencies:** Modules are independent
- **Testable:** Each module has its own test file

## 🚦 Migration Notes
- Legacy code in `gpt_service.py` is being phased out. Use shared modules for new features and refactors.
- If you need a new shared utility, add it here and update `__init__.py`.

## 🏁 Quick Start
1. Add your shared function to the appropriate module
2. Export it in `__init__.py`
3. Import it in your service file as shown above
4. Add or update tests in the corresponding test file

---
For questions, see `PHASE_2_COMPLETION_SUMMARY.md` or contact the system architect.
