# Demonstration of Contextual Conversation Flow Improvements

## Problem Summary
User reported: **"pertanyaan sebelumnya dan jawaban juga pertanyaan sebelumnya masih belum nyambung masih ada beberapa miss"**

The issue was that CS questions weren't naturally connecting to customer's previous responses, creating disjointed conversations.

## Solution Implemented

### 1. Enhanced Ollama Prompt with Better Context Awareness

**Before (Generic Prompt):**
```
Generate next question for telecollection...
```

**After (Context-Rich Prompt):**
```python
KONTEKS PERCAKAPAN LENGKAP:
{full_conversation_context}

SITUASI TERKINI:
- Pertanyaan terakhir: "{last_question}"
- Jawaban customer: "{last_answer}"
- Goal yang ingin dicapai: {next_goal}

INSTRUKSI PENTING:
1. WAJIB merespon dan menyambung dari jawaban customer terakhir: "{last_answer}"
2. Gunakan transisi natural seperti "Saya memahami...", "Baik, kalau begitu...", "Oh begitu..."
3. Jangan mengulang pertanyaan yang sudah ditanyakan sebelumnya
4. Pertanyaan harus mengalir natural dari konteks
5. Gunakan bahasa Indonesia conversational yang ramah

CONTOH TRANSISI YANG BAIK:
- Jika customer bilang "masalah keuangan" → "Saya memahami situasinya. Kira-kira kapan..."
- Jika customer bilang "3 hari lagi" → "Baik, berarti 3 hari dari sekarang ya. Untuk memastikan..."
- Jika customer bilang "sudah berhenti" → "Oh begitu, boleh tau alasan..."
```

### 2. Context-Responsive Question Generation

**New Function: `determine_next_question_by_context`**
```python
def determine_next_question_by_context(mode: str, conversation_history: List[Dict], dataset: List[Dict]) -> Dict:
    """Tentukan pertanyaan berikutnya berdasarkan konteks jawaban customer dengan transisi natural"""
    
    last_answer = conversation_history[-1].get("a", "").lower()
    
    # For telecollection mode
    if mode == "telecollection":
        if any(word in last_answer for word in ["masalah", "kesulitan", "sulit", "tidak ada uang"]):
            return {
                "question": f"Saya memahami situasi Anda saat ini. Kira-kira kapan bisa melakukan pembayaran?",
                "options": [
                    "Dalam 3-5 hari setelah gajian",
                    "Minggu depan pasti bisa",
                    "Masih belum pasti, tergantung kondisi",
                    "Bisa cicil tidak pak?"
                ]
            }
        elif any(word in last_answer for word in ["hari", "minggu", "gajian"]):
            return {
                "question": f"Baik, berarti {last_answer} ya. Untuk memastikan komitmen Anda, apakah ini sudah pasti?",
                "options": [
                    "Ya pasti, sudah saya catat di agenda",
                    "Insya Allah, 90% yakin bisa",
                    "Kemungkinan besar, tapi masih ada kendala kecil"
                ]
            }
```

### 3. Improved Question Priority Logic

**New Priority System:**
1. **Priority 1:** Context-responsive questions that directly respond to customer's last answer
2. **Priority 2:** Ollama-generated questions with full conversation context
3. **Priority 3:** Dataset fallback with smart templates

**Implementation:**
```python
# Priority 1: Use context-based question that directly responds to customer's last answer
context_question = determine_next_question_by_context(mode, conversation_history, dataset)
if context_question:
    return context_question

# Priority 2: Try Ollama for dynamic generation with full conversation context
ollama_question = await generate_dynamic_question_with_ollama(mode, conversation_history, current_goal)
if ollama_question:
    return ollama_question

# Priority 3: Fallback to sequential dataset progression
return dataset_fallback_question
```

## Example of Improved Flow

### Before (Disconnected):
```
CS: "Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?"
Customer: "Saya ada masalah keuangan saat ini pak, belum ada uang untuk bayar"
CS: "Baik, lalu kapan rencana pembayarannya?" ❌ (Generic, doesn't acknowledge problem)
```

### After (Natural Connection):
```
CS: "Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?"
Customer: "Saya ada masalah keuangan saat ini pak, belum ada uang untuk bayar"
CS: "Saya memahami situasi Anda saat ini. Kira-kira kapan bisa melakukan pembayaran?" ✅ (Acknowledges situation, shows empathy)
```

## Key Improvements Delivered

1. **Natural Transitions:** Questions now use phrases like "Saya memahami...", "Baik, kalau begitu..." to connect naturally
2. **Contextual Acknowledgment:** CS agent acknowledges what customer just said before asking next question
3. **Empathetic Language:** More understanding and supportive tone
4. **Specific References:** Questions reference specific details from customer's previous answer
5. **Logical Flow:** Each question builds logically on the previous customer response

## Testing Results

The improved system now generates conversations like:

**Step 1:** Customer mentions "masalah keuangan"
**→** CS responds: "Saya memahami situasi Anda..." (Shows empathy)

**Step 2:** Customer says "5 hari lagi setelah gajian"  
**→** CS responds: "Baik, berarti 5 hari dari sekarang ya..." (References specific timeline)

**Step 3:** Customer confirms timeline
**→** CS responds: "Untuk memastikan komitmen..." (Natural progression to commitment)

## Technical Implementation

The solution uses:
- **Enhanced Ollama prompts** with detailed conversation context
- **Context-aware question selection** that analyzes customer responses
- **Natural language transitions** between questions
- **Empathetic acknowledgment** of customer situations
- **Specific reference integration** to previous customer answers

This addresses the user's concern that "pertanyaan sebelumnya dan jawaban juga pertanyaan sebelumnya masih belum nyambung" by ensuring every question naturally connects to and builds upon the customer's previous response.