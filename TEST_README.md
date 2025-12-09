# 🤖 SISTEM PERCAKAPAN CS ICONNET - Enhanced with Ollama AI

## 🚀 NEW FEATURES: Dynamic Question Generation

Sistem sekarang menggunakan **Ollama AI** untuk menghasilkan pertanyaan yang dinamis dan kontekstual berdasarkan jawaban customer!

### ✨ Fitur Terbaru:
- **🧠 AI-Powered Questions**: Ollama menganalisis jawaban customer dan menghasilkan pertanyaan follow-up yang relevan
- **🔄 Context-Aware Flow**: Sistem mengingat informasi dari percakapan sebelumnya
- **⚡ Real-time Generation**: Pertanyaan dihasilkan secara real-time berdasarkan konteks
- **🛡️ Fallback System**: Jika Ollama tidak tersedia, sistem akan menggunakan flow tradisional

### 🎯 Conversation Topics:
1. **Telecollection** - Penagihan & Recovery
2. **Winback** - Reaktivasi Customer  
3. **Retention** - Pencegahan Churn

---

## 🔧 SETUP REQUIREMENTS

### 1. Ollama Installation
```bash
# Install Ollama (Windows/Mac/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Download and run Llama2 model
ollama pull llama2
ollama serve
```

### 2. Environment Configuration
Pastikan `.env` file berisi:
```properties
OLLAMA_API_URL=http://localhost:11434
```

### 3. Start Services
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3: Start Frontend  
cd frontend
npm run dev
```

---

## 🧪 TESTING SCENARIOS

### SCENARIO 1 - TELECOLLECTION (AI-Enhanced):
```
CS: "Selamat siang, saya dari ICONNET. Apakah sudah melakukan pembayaran bulanan?"
Customer: "Belum bayar, masih kesulitan keuangan"
AI: "Saya memahami situasi Bapak/Ibu. Apakah ada opsi pembayaran yang lebih fleksibel yang bisa membantu?"
```

### SCENARIO 2 - WINBACK (AI-Enhanced):
```
CS: "Layanan ICONNET Bapak/Ibu terputus. Ada kendala yang bisa kami bantu?"
Customer: "Internet sering putus, tidak puas dengan layanan"
AI: "Mohon maaf atas ketidaknyamanannya. Tim teknis kami sudah melakukan perbaikan. Dengan layanan yang sudah diperbaiki dan promo khusus, apakah Bapak/Ibu bersedia mencoba lagi?"
```

### SCENARIO 3 - RETENTION (AI-Enhanced):
```
CS: "Bagaimana pengalaman menggunakan layanan ICONNET selama ini?"
Customer: "Kadang lambat saat malam hari, tapi overall OK"
AI: "Terima kasih feedbacknya! Untuk masalah kecepatan malam hari, kami punya upgrade paket yang bisa mengatasi hal tersebut. Apakah Bapak/Ibu tertarik mendengar detailnya?"
```

---

## 🤖 HOW AI WORKS

### 1. **Context Analysis**
Ollama menganalisis:
- Jawaban customer sebelumnya
- Sentiment dan intent
- Key information (tanggal, nominal, alasan)
- Response patterns

### 2. **Dynamic Question Generation**
```javascript
// AI menghasilkan pertanyaan berdasarkan konteks
{
  "question": "Pertanyaan yang disesuaikan dengan jawaban customer",
  "options": ["Opsi yang relevan", "Berdasarkan konteks", "Jawaban sebelumnya"],
  "reasoning": "Alasan AI memilih pertanyaan ini",
  "stage": "opening/middle/closing"
}
```

### 3. **Smart Branching**
- Sistem otomatis mengarahkan percakapan
- Mengingat informasi penting
- Menyesuaikan tone berdasarkan customer response

---

## 🎮 TESTING FEATURES

### Test AI Response:
1. **Positive Response**: "Ya, saya tertarik dengan promo"
   - Expected: AI akan menanyakan detail lebih lanjut tentang promo
   
2. **Negative Response**: "Tidak, saya tidak tertarik"
   - Expected: AI akan menggali alasan dan mencari solusi alternatif
   
3. **Uncertain Response**: "Saya masih berpikir"
   - Expected: AI akan memberikan informasi tambahan untuk membantu keputusan

### Test Error Handling:
- Matikan Ollama service
- Expected: Sistem akan menggunakan fallback questions
- Show message: "AI generation temporarily unavailable"

---

## 🔍 MONITORING & DEBUGGING

### Console Logs:
```
🤖 Generating next question with Ollama...
✅ Setting new question from Ollama: [pertanyaan]
📊 Prediction result: [hasil prediksi]
❌ Error in handleAnswer: [jika ada error]
```

### Check Ollama Status:
```bash
curl http://localhost:11434/api/tags
```

---

## 📊 EXPECTED IMPROVEMENTS

### Before AI:
- ❌ Pertanyaan statis dan tidak fleksibel
- ❌ Tidak mempertimbangkan konteks jawaban
- ❌ Flow yang kaku dan terprediksi

### After AI:
- ✅ Pertanyaan dinamis dan kontekstual
- ✅ Mengingat informasi dari percakapan sebelumnya  
- ✅ Adaptif terhadap jawaban customer
- ✅ Professional tone yang konsisten
- ✅ Better customer experience

---

🎉 **System is ready! Start conversation simulation with enhanced AI capabilities!**