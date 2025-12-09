# Developer Quick-Start Guide: Shared Utilities

Welcome to the ICONNET Percakapan System shared utilities! This guide helps you quickly use, extend, and test the shared modules.

## 1. Import Shared Functions
Import directly in your service file:
```python
from .shared.risk_calculator import compute_risk_level
from .shared.sentiment_analyzer import analyze_sentiment_and_intent
from .shared.date_utils import get_current_date_info
from .shared.ollama_client import generate_reason_with_ollama
```

## 2. Add a New Shared Utility
- Create your function in the appropriate module (or a new one in `shared/`)
- Export it in `shared/__init__.py`
- Add a test in the corresponding test file (e.g., `test_risk_calculator_extraction.py`)

## 3. Run All Tests
To verify everything works:
```powershell
python test_phase2_integration.py
```
Or run individual module tests:
```powershell
python test_risk_calculator_extraction.py
python test_sentiment_analyzer_extraction.py
python test_date_utils_extraction.py
python test_data_persistence_extraction.py
python test_ollama_simple.py
```

## 4. Migration Tips
- Use shared modules for all new features and refactors
- Legacy code in `gpt_service.py` is being phased out
- If you find duplicate logic, move it to shared and update imports

## 5. Documentation
- See `backend/app/services/shared/README.md` for architecture
- See `PHASE_2_COMPLETION_SUMMARY.md` for migration details
- See `POST_PHASE2_VERIFICATION.md` for test results

---
For help, contact the system architect or check the documentation above.
