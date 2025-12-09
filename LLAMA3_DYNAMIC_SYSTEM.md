# 🤖 Dynamic Question Generation dengan Llama3

## 📋 Overview

Sistem sekarang sudah **FULLY DYNAMIC** dengan Llama3! Pertanyaan tidak lagi statis dari dataset, tapi di-generate secara real-time berdasarkan konteks percakapan.

## ✅ Fitur yang Sudah Diimplementasikan

### 1. **Context Memory** ✅
- Semua riwayat percakapan disimpan di `conversation_history`
- Sistem mengambil 3 percakapan terakhir untuk konteks

### 2. **Goal Engine** ✅
- `determine_next_goal()` - Menentukan goal berikutnya
- `determine_winback_next_goal()` - Branching logic untuk winback
- Flow otomatis menyesuaikan berdasarkan jawaban user

### 3. **Llama3 Dynamic Generation** ✅ NEW!
- Fungsi: `generate_dynamic_question_with_llama3()`
- Generate pertanyaan real-time berdasarkan konteks
- Fallback ke static question jika Llama3 gagal

### 4. **Few-Shot Learning** ✅ NEW!
- Load contoh percakapan dari CSV: `training_data.csv`
- Llama3 belajar pola dari contoh real
- Maksimal 2-3 contoh per goal untuk efisiensi

### 5. **Intelligent Fallback** ✅
```
Llama3 Dynamic → Static Dataset → Ultimate Fallback
```

## 🏗️ Arsitektur Sistem

```
User Answer
    ↓
[Context Manager]
    ↓
[Goal Engine] → determine_next_goal()
    ↓
[Llama3 Generator] ← Few-Shot Examples (CSV)
    ↓
Dynamic Question
    ↓
User
```

## 📝 Cara Menggunakan

### 1. Install Ollama & Pull Llama3

```bash
# Install Ollama
# Download dari https://ollama.ai

# Pull model Llama3
ollama pull llama3
```

### 2. Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 3. Test Dynamic Generation

Sistem akan otomatis menggunakan Llama3 jika:
- Ollama running di `http://localhost:11434`
- Model `llama3` sudah di-pull
- Ada conversation history (> 0 exchanges)

## 📊 Training Data Format

File: `backend/app/dataset/training_data.csv`

```csv
goal,question,answer,context,mode
status_contact,"Halo! Untuk pembayaran bulanan ICONNET bulan ini udah diselesaikan belum ya?","Belum bayar","Customer belum melakukan pembayaran",telecollection
payment_barrier,"Ada kendala khusus yang membuat pembayaran tertunda?","Belum gajian","Customer menunggu gaji",telecollection
```

**Kolom:**
- `goal`: Goal percakapan (status_contact, payment_barrier, dll)
- `question`: Contoh pertanyaan CS
- `answer`: Contoh jawaban customer
- `context`: Konteks situasi
- `mode`: telecollection / winback

## 🔧 Konfigurasi

File: `backend/app/services/gpt_service.py`

```python
# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
OLLAMA_TIMEOUT = 12
OLLAMA_MODEL = "llama3"  # Model untuk dynamic generation
```

## 🎯 Cara Kerja Dynamic Generation

### Step 1: User Menjawab
```
User: "Belum bayar, lagi tunggu gajian"
```

### Step 2: System Analyze Context
```python
conversation_history = [
    {"q": "Untuk pembayaran bulan ini sudah?", "a": "Belum bayar, lagi tunggu gajian"}
]
goal_status = {"status_contact": achieved}
next_goal = "payment_barrier"  # Determined by goal engine
```

### Step 3: Llama3 Generate Question
```python
# Load few-shot examples
examples = load_from_csv(goal="payment_barrier")

# Send to Llama3
prompt = """
Konteks: Customer belum bayar, tunggu gajian
Goal: payment_barrier (tanyakan kendala spesifik)
Examples: [2 contoh dari CSV]

Generate pertanyaan berikutnya...
"""

# Llama3 Response
question = "Oke, berarti nunggu tanggal gajian ya? Kira-kira tanggalnya kapan?"
options = ["Tanggal 25", "Awal bulan depan", "Minggu depan", "Belum pasti"]
```

### Step 4: Return to User
```
CS: "Oke, berarti nunggu tanggal gajian ya? Kira-kira tanggalnya kapan?"
Options: Tanggal 25 | Awal bulan depan | Minggu depan | Belum pasti
```

## 📈 Meningkatkan Akurasi

### 1. Tambah Training Data

Edit `training_data.csv`, tambahkan lebih banyak contoh:

```csv
payment_timeline,"Kapan bisa bayar?","Besok pagi","Customer komitmen besok",telecollection
payment_timeline,"Target pembayarannya?","Akhir minggu ini","Customer komitmen minggu ini",telecollection
```

### 2. Tuning Prompt

Edit system prompt di fungsi `generate_dynamic_question_with_llama3()`:

```python
system_prompt = f"""Kamu adalah Customer Service ICONNET yang profesional dan ramah.

GAYA BICARA:
- Santai tapi profesional
- Empati tinggi
- Singkat dan to-the-point

ATURAN:
...
"""
```

### 3. Adjust Few-Shot Count

```python
# Default: 2 examples
few_shot_examples = load_few_shot_examples(goal=goal, mode=mode, max_examples=3)  # Ubah jadi 3
```

## 🐛 Troubleshooting

### Llama3 Tidak Generate Question?

**Check Logs:**
```
[LLAMA3] Generating dynamic question for goal: payment_barrier
[LLAMA3 SUCCESS] Generated: ...
```

Atau:
```
[LLAMA3 ERROR] Status code: 500
[LLAMA3 FALLBACK] Using static question...
```

**Solusi:**
1. Pastikan Ollama running: `ollama list`
2. Test manual: `ollama run llama3 "hello"`
3. Check timeout: Increase `OLLAMA_TIMEOUT` jika koneksi lambat

### Question Tidak Natural?

**Solusi:**
1. Tambah lebih banyak contoh di `training_data.csv`
2. Improve system prompt dengan gaya yang diinginkan
3. Filter examples yang lebih relevan dengan goal

### Slow Response?

**Solusi:**
1. Reduce `max_examples` di few-shot loading (2 → 1)
2. Reduce conversation context (3 → 2 last exchanges)
3. Use smaller model: `llama3.2` instead of `llama3`

## 📊 Monitoring

### Check Llama3 Usage

```python
# Di endpoint atau console
from app.services.gpt_service import OLLAMA_STATS

print(OLLAMA_STATS)
# {
#     "total_calls": 15,
#     "successful_calls": 14,
#     "quality_scores": [0.85, 0.90, ...],
#     "avg_response_time": 1.2
# }
```

## 🚀 Next Steps

### 1. Add More Training Data
- Kumpulkan percakapan real dari CS
- Export ke CSV format
- System akan auto-improve

### 2. Model Fine-tuning (Advanced)
```bash
# Create fine-tuning dataset
ollama create iconnet-cs -f Modelfile

# Modelfile content:
FROM llama3
SYSTEM "You are ICONNET customer service..."
```

### 3. A/B Testing
- Compare static vs dynamic questions
- Track conversion rate per mode
- Optimize based on data

## 📞 Support

Jika ada pertanyaan atau issues:
1. Check logs di terminal backend
2. Verify Ollama status: `ollama ps`
3. Test Llama3 manual: `ollama run llama3`

---

**Status:** ✅ FULLY IMPLEMENTED & PRODUCTION READY

Sistem sekarang 100% sesuai dengan konsep yang Anda berikan! 🎉
