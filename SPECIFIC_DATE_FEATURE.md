# Feature Implementation: Specific Date Request for "Akhir Bulan" & "Awal Bulan"

## Problem Statement
**User Request:** "ketika memilih akhir bulan minta tanggal pastinya"

When customers say "akhir bulan" (end of month) or "awal bulan" (beginning of month), the system should ask for more specific dates instead of accepting vague timeframes.

## Solution Implemented

### 1. Enhanced Context Detection in `determine_next_question_by_context`

**Added Detection for "Akhir Bulan":**
```python
elif any(word in last_answer for word in ["akhir bulan", "tanggal tua", "end of month"]):
    return {
        "id": "tc_context_specific_date",
        "question": f"Baik, berarti akhir bulan ya. Untuk lebih spesifik, kira-kira tanggal berapa di akhir bulan ini?",
        "options": [
            "Tanggal 25-27 bulan ini",
            "Tanggal 28-30 bulan ini", 
            "Tanggal 31 pasti",
            "Paling lambat tanggal 30"
        ],
        "goal": "specific_date_confirmation"
    }
```

**Added Detection for "Awal Bulan":**
```python
elif any(word in last_answer for word in ["awal bulan", "beginning of month"]):
    return {
        "id": "tc_context_early_date",
        "question": f"Baik, berarti awal bulan depan ya. Untuk lebih spesifik, kira-kira tanggal berapa di awal bulan?",
        "options": [
            "Tanggal 1-3 bulan depan",
            "Tanggal 5-7 bulan depan",
            "Tanggal 10 paling lambat",
            "Setelah gajian turun (tanggal 5)"
        ],
        "goal": "early_date_confirmation"
    }
```

### 2. Follow-up Date Commitment Logic

**Added handling for specific date responses:**
```python
elif conversation_length == 2:
    # After specific date question for "akhir bulan" or "awal bulan"
    if any(word in last_answer for word in ["tanggal", "1", "2", "3", "5", "7", "10", "25", "26", "27", "28", "29", "30", "31"]):
        return {
            "id": "tc_context_date_commit",
            "question": f"Baik, berarti {last_answer} ya. Untuk memastikan komitmen pembayaran pada tanggal tersebut, apakah sudah pasti bisa?",
            "options": [
                "Ya pasti, sudah saya catat tanggalnya",
                "Insya Allah bisa pada tanggal itu",
                "Kemungkinan besar, tapi mungkin 1-2 hari setelahnya",
                "Masih belum 100% pasti"
            ],
            "goal": "date_commitment"
        }
```

### 3. Enhanced Ollama AI Prompt with Date Rules

**Added specific instructions for Ollama:**
```python
ATURAN KHUSUS:
- Jika customer menyebutkan "akhir bulan", "tanggal tua", "end of month" → WAJIB tanya tanggal spesifik (25-31)
- Jika customer menyebutkan "awal bulan" → WAJIB tanya tanggal spesifik (1-10)

CONTOH TRANSISI YANG BAIK:
- Jika customer bilang "akhir bulan" → "Baik, akhir bulan ya. Untuk lebih spesifik, kira-kira tanggal berapa..."
```

## Example Conversation Flow

### Before (Vague):
```
CS: "Kapan bisa melakukan pembayaran?"
Customer: "Akhir bulan ini pak"
CS: "Baik, akhir bulan. Apakah yakin bisa tepat waktu?" ❌ (Accepts vague timeframe)
```

### After (Specific):
```
CS: "Kapan bisa melakukan pembayaran?"
Customer: "Akhir bulan ini pak"
CS: "Baik, berarti akhir bulan ya. Untuk lebih spesifik, kira-kira tanggal berapa di akhir bulan ini?" ✅

Customer: "Tanggal 28-30 bulan ini pak"
CS: "Baik, berarti tanggal 28-30 bulan ini ya. Untuk memastikan komitmen pembayaran pada tanggal tersebut, apakah sudah pasti bisa?" ✅
```

## Complete Flow Scenarios

### Scenario 1: "Akhir Bulan" → Specific Date
1. **Customer:** "Akhir bulan ini pak"
2. **CS:** "Baik, berarti akhir bulan ya. Untuk lebih spesifik, kira-kira tanggal berapa di akhir bulan ini?"
   - Options: ["Tanggal 25-27 bulan ini", "Tanggal 28-30 bulan ini", "Tanggal 31 pasti", "Paling lambat tanggal 30"]
3. **Customer:** "Tanggal 28-30 bulan ini pak"
4. **CS:** "Baik, berarti tanggal 28-30 bulan ini ya. Untuk memastikan komitmen pembayaran pada tanggal tersebut, apakah sudah pasti bisa?"

### Scenario 2: "Awal Bulan" → Specific Date
1. **Customer:** "Awal bulan depan pak"
2. **CS:** "Baik, berarti awal bulan depan ya. Untuk lebih spesifik, kira-kira tanggal berapa di awal bulan?"
   - Options: ["Tanggal 1-3 bulan depan", "Tanggal 5-7 bulan depan", "Tanggal 10 paling lambat", "Setelah gajian turun (tanggal 5)"]
3. **Customer:** "Tanggal 5-7 bulan depan pak"
4. **CS:** "Baik, berarti tanggal 5-7 bulan depan ya. Untuk memastikan komitmen pembayaran pada tanggal tersebut, apakah sudah pasti bisa?"

## Technical Implementation Details

### Files Modified:
- **`backend/app/services/gpt_service.py`**
  - Enhanced `determine_next_question_by_context()` function
  - Added specific date detection logic
  - Updated Ollama prompt with date-specific rules

### Key Features:
1. **Automatic Detection:** System automatically detects "akhir bulan" and "awal bulan" phrases
2. **Specific Date Ranges:** Provides relevant date range options (25-31 for end of month, 1-10 for beginning)
3. **Commitment Confirmation:** After getting specific dates, asks for commitment confirmation
4. **Natural Language Flow:** Uses natural transitions like "Baik, berarti... ya"
5. **Dual System Support:** Works with both context-based logic and Ollama AI

### Benefits:
- **More Precise Scheduling:** Gets specific dates instead of vague timeframes
- **Better Follow-up:** CS can schedule more accurate follow-up calls
- **Improved Collection Rate:** Specific commitments lead to better payment compliance
- **Natural Conversation:** Maintains conversational flow while getting specific information

## Status: ✅ IMPLEMENTED

The feature is now active and will automatically prompt for specific dates whenever customers mention "akhir bulan" or "awal bulan" in their payment timeline responses.