# 📋 Panduan Restrukturisasi gpt_service.py

## 🎯 Tujuan
Mereorganisasi `gpt_service.py` agar lebih mudah dibaca dan dimaintain dengan memisahkan:
1. **Data & Constants** (pertanyaan, goals) - paling atas
2. **Telecollection Functions**
3. **Winback Functions**  
4. **Shared/Utility Functions** - paling bawah

## 📊 Struktur Baru

```
gpt_service.py
│
├─ SECTION 1: IMPORTS & EXPORTS
│  └─ Import libraries & __all__ export list
│
├─ SECTION 2: TELECOLLECTION DATA & CONSTANTS
│  ├─ TELECOLLECTION_GOALS
│  ├─ TELECOLLECTION_QUESTIONS
│  └─ Telecollection-specific constants
│
├─ SECTION 3: WINBACK DATA & CONSTANTS
│  ├─ WINBACK_QUESTIONS
│  ├─ CONVERSATION_GOALS
│  └─ Winback-specific constants
│
├─ SECTION 4: TELECOLLECTION FUNCTIONS
│  ├─ generate_telecollection_question()
│  ├─ check_telecollection_goals()
│  ├─ predict_telecollection_outcome()
│  └─ Telecollection-specific functions
│
├─ SECTION 5: WINBACK FUNCTIONS
│  ├─ generate_winback_question()
│  ├─ determine_winback_next_goal()
│  ├─ check_winback_goals()
│  ├─ predict_winback_outcome()
│  └─ Winback-specific functions
│
└─ SECTION 6: SHARED/UTILITY FUNCTIONS
   ├─ analyze_sentiment_and_intent()
   ├─ generate_question() (router)
   ├─ check_conversation_goals() (router)
   ├─ save_conversation_to_excel()
   ├─ get_current_date_info()
   └─ Other utility functions
```

## 🔍 Identifikasi Fungsi

### Telecollection Functions (Pindahkan ke Section 4)
- `generate_telecollection_question()`
- `predict_telecollection_outcome()`
- `check_telecollection_goals()` (jika ada fungsi khusus)
- Fungsi lain yang hanya dipakai untuk telecollection

### Winback Functions (Pindahkan ke Section 5)
- `generate_winback_question()`
- `determine_winback_next_goal()`
- `check_winback_goals()`
- `predict_winback_outcome()`
- `get_reason_inquiry_question()`
- `get_equipment_check_question()`
- Fungsi lain yang hanya dipakai untuk winback

### Shared Functions (Tetap di Section 6)
- `analyze_sentiment_and_intent()`
- `generate_question()` - router yang memanggil telecollection/winback
- `check_conversation_goals()` - router yang memanggil telecollection/winback
- `generate_question_for_goal()`
- `determine_next_goal()`
- `save_conversation_to_excel()`
- `get_current_date_info()`
- `parse_relative_date()`
- `get_question_from_dataset()`
- `generate_automatic_customer_answer()`
- `predict_status_promo_ollama()`
- `predict_status_promo_svm()`
- `predict_status_promo_lda()`
- Utility functions lainnya

## 📝 Langkah-Langkah Restrukturisasi

### Opsi 1: Manual (Disarankan untuk kontrol penuh)

1. **Backup file asli**
   ```bash
   cp gpt_service.py gpt_service_BACKUP.py
   ```

2. **Buat file baru dengan header**
   - Copy section 1 (imports & exports) dari template
   - Copy section 2 (telecollection data) dari file asli
   - Copy section 3 (winback data) dari file asli

3. **Pindahkan fungsi telecollection** (Section 4)
   - Cari semua fungsi dengan nama `*telecollection*`
   - Copy ke section 4
   - Tambahkan comment separator antar fungsi

4. **Pindahkan fungsi winback** (Section 5)
   - Cari semua fungsi dengan nama `*winback*`
   - Copy ke section 5
   - Tambahkan comment separator antar fungsi

5. **Pindahkan shared functions** (Section 6)
   - Copy semua fungsi yang tersisa
   - Urutkan berdasarkan fungsi (sentiment, question generation, prediction, utilities)

6. **Test & verify**
   ```bash
   # Test import
   python -c "from app.services.gpt_service import *"
   
   # Run tests
   pytest tests/
   ```

### Opsi 2: Menggunakan Script Python

Buat script `restructure.py`:

```python
import re

def extract_functions(content, pattern):
    """Extract functions matching pattern"""
    functions = []
    # Regex to find function definitions
    func_pattern = r'def ' + pattern + r'\(.*?\):'
    # ... implementation
    return functions

# Read original file
with open('gpt_service.py', 'r', encoding='utf-8') as f:
    original_content = f.read()

# Extract sections
telecollection_funcs = extract_functions(original_content, '.*telecollection.*')
winback_funcs = extract_functions(original_content, '.*winback.*')
# ... etc

# Write to new file with structure
# ... implementation
```

## ✅ Checklist Verifikasi

- [ ] Semua imports masih berfungsi
- [ ] `__all__` export list complete
- [ ] TELECOLLECTION_QUESTIONS & TELECOLLECTION_GOALS ada di Section 2
- [ ] WINBACK_QUESTIONS & CONVERSATION_GOALS ada di Section 3
- [ ] Fungsi telecollection di Section 4
- [ ] Fungsi winback di Section 5
- [ ] Shared functions di Section 6
- [ ] Tidak ada duplikasi fungsi
- [ ] Test suite passed
- [ ] API endpoints masih berfungsi

## 🔧 Tips

1. **Gunakan comment separator yang jelas**
   ```python
   # =====================================================
   # 📞 TELECOLLECTION: Question Generation
   # =====================================================
   ```

2. **Group fungsi related berdekatan**
   ```python
   # Question generation
   def generate_telecollection_question(): ...
   
   # Goal checking
   def check_telecollection_goals(): ...
   
   # Prediction
   def predict_telecollection_outcome(): ...
   ```

3. **Tambahkan docstring yang jelas**
   ```python
   def generate_telecollection_question(goal: str, context: dict) -> dict:
       """
       🎯 TELECOLLECTION: Generate question for specific goal
       
       Args:
           goal: Goal name (status_contact, payment_barrier, payment_timeline)
           context: Conversation context
           
       Returns:
           Question data with options
       """
   ```

4. **Test incrementally**
   - Setiap selesai pindahkan satu section, test import
   - Jangan pindahkan semua sekaligus

## 📄 File Template

Gunakan `gpt_service_RESTRUCTURED.py` sebagai template starting point.

## 🆘 Troubleshooting

**Problem:** Import error setelah restruktur
**Solution:** Cek `__all__` list, pastikan semua fungsi exported

**Problem:** Circular import
**Solution:** Pastikan shared functions di paling bawah

**Problem:** Fungsi tidak ditemukan
**Solution:** Cek apakah sudah dipindahkan atau masih di file asli

## 📞 Contact

Jika ada pertanyaan atau butuh bantuan, silakan hubungi tim development.
