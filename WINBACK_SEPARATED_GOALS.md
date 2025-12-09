🎯 WINBACK GOALS SEPARATION - COMPLETE UPDATE
======================================================

## ✅ CHANGES IMPLEMENTED

### 1️⃣ **NEW GOALS STRUCTURE**
**File**: `backend/app/services/gpt_service.py`

**BEFORE** (5 goals):
```python
"winback": ["greeting_identity", "identity_confirmation", "promo_offer", "response_handling", "closing"]
```

**AFTER** (7 goals):
```python
"winback": ["greeting_identity", "identity_confirmation", "promo_offer", "response_handling", "reason_inquiry", "equipment_check", "closing"]
```

### 2️⃣ **SEPARATED QUESTIONS**

#### **REASON INQUIRY QUESTIONS** (New Category):
```python
"reason_inquiry": [
    {
        "id": "wb_reason_001",
        "question": "Baik Bapak/Ibu, jika boleh tahu karena apa ya tidak bersedia mengaktifkan kembali layanan ICONNET?",
        "options": ["Pindah rumah", "Ada keluhan layanan", "Tidak butuh internet", "Alasan keuangan"]
    },
    {
        "id": "wb_reason_002",
        "question": "Baik, boleh share lebih detail apa kendala yang dialami selama berlangganan ICONNET?",
        "options": ["Sering putus", "Kecepatan lambat", "Pelayanan CS kurang", "Harga terlalu mahal"]
    }
]
```

#### **EQUIPMENT CHECK QUESTIONS** (New Category):
```python
"equipment_check": [
    {
        "id": "wb_equip_001", 
        "question": "Baik Bapak/Ibu, untuk perangkat ICONNET-nya apakah masih berada di lokasi rumah?",
        "options": ["Masih ada", "Sudah dikembalikan", "Hilang/rusak", "Tidak tahu"]
    },
    {
        "id": "wb_equip_002",
        "question": "Untuk perangkat yang masih ada, kondisinya bagaimana ya? Masih berfungsi dengan baik?",
        "options": ["Normal semua", "Ada yang rusak", "Belum dicoba", "Tidak yakin"]
    },
    {
        "id": "wb_equip_003",
        "question": "Baik, kalau perangkat sudah dikembalikan, untuk lokasi saat ini apakah sudah terpasang internet lain?",
        "options": ["Sudah pakai provider lain", "Belum ada internet", "Pakai mobile data saja", "Masih cari provider"]
    }
]
```

### 3️⃣ **UPDATED RESPONSE_HANDLING**
**BEFORE**: Combined reason + equipment question:
```python
"question": "Baik Bapak/Ibu, jika boleh tahu karena apa ya? Apakah perangkatnya masih berada di lokasi?"
```

**AFTER**: Only reason question:
```python
"question": "Baik Bapak/Ibu, jika boleh tahu karena apa ya tidak bersedia mengaktifkan kembali?"
```

### 4️⃣ **ENHANCED GOAL DETECTION**
Added detection for new goals:
```python
# Detect reason_inquiry
elif any(phrase in question_lower for phrase in ["jika boleh tahu karena apa", "tidak bersedia mengaktifkan", "kendala yang dialami"]):
    goal_results["reason_inquiry"] = {"achieved": True, "score": 85}

# Detect equipment_check  
elif any(phrase in question_lower for phrase in ["perangkat iconnet", "masih berada di lokasi", "kondisinya bagaimana", "sudah dikembalikan"]):
    goal_results["equipment_check"] = {"achieved": True, "score": 85}
```

### 5️⃣ **BRANCHING LOGIC UPDATE**
Enhanced flow for rejection handling:
```python
# After promo rejection → reason inquiry
elif any(word in last_answer for word in ["tidak", "tolak", "gak"]):
    print("[BRANCH] Rejected → reason inquiry")  
    return "reason_inquiry"

# After reason inquiry → equipment check
if not goal_status.get('equipment_check', {}).get('achieved', False):
    return "equipment_check"
```

### 6️⃣ **NEW HELPER FUNCTIONS**
Added specialized question generators:
- `get_reason_inquiry_question()` - Smart reason question selection
- `get_equipment_check_question()` - Context-aware equipment questions

## 📊 **FLOW COMPARISON**

### **OLD FLOW** (Combined):
1. Identity Confirmation ✅
2. Promo Offer ✅  
3. Response Handling ✅ *(includes reason + equipment)*
4. Closing ✅

### **NEW FLOW** (Separated):
1. Identity Confirmation ✅
2. Promo Offer ✅
3. Response Handling ✅ *(payment timeline for acceptance)*
4. **Reason Inquiry** ✅ *(separate reason questions)*
5. **Equipment Check** ✅ *(separate equipment questions)*
6. Closing ✅

## 🎯 **BENEFITS**

✅ **Better Data Collection**: Separate tracking for reason vs equipment status
✅ **Improved Analytics**: Distinct metrics for cancellation reasons and equipment recovery
✅ **Enhanced Branching**: More specific follow-up based on reason type
✅ **Modular Questions**: Individual question categories for better maintainability
✅ **Progress Tracking**: More granular goal completion (7 steps vs 5 steps)

## 📋 **TESTING STATUS**

✅ **Goals Structure**: 7 goals properly defined
✅ **Question Categories**: Reason inquiry (2) + Equipment check (3) questions added
✅ **Question Generation**: Both new goal types generate questions successfully
✅ **Goal Detection**: Enhanced detection for new question types
✅ **Branching Logic**: Proper flow from promo rejection → reason → equipment

## 🚀 **READY FOR USE**

**Impact**: Sistema winback sekarang memisahkan pertanyaan alasan dan perangkat menjadi 2 goals terpisah, memungkinkan tracking yang lebih detail dan branching logic yang lebih spesifik untuk setiap jenis response.

**Next Steps**: Test dengan conversation nyata untuk memastikan flow berjalan sesuai ekspektasi dengan goals yang terpisah.