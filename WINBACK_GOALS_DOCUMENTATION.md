# WINBACK GOALS IMPLEMENTATION
## Berdasarkan Flow Diagram yang Diberikan

### 📋 Goals Structure

Berdasarkan alur diagram yang diberikan, goals winback telah diupdate menjadi 5 tahapan utama:

```python
CONVERSATION_GOALS = {
    "winback": [
        "service_status",       # Cek status layanan customer
        "stop_reason",          # Tanyakan alasan berhenti
        "network_issues",       # Handle masalah teknis
        "promo_offer",          # Tawarkan promo
        "interest_confirmation" # Konfirmasi minat
    ]
}
```

### 🎯 Goal Flow Mapping

#### 1. **SERVICE_STATUS** - Status Layanan
- **Tujuan**: Mengecek apakah customer masih menggunakan layanan
- **Opsi Jawaban**: 
  - Ya, masih pakai
  - Sudah tidak pakai
  - Sudah berhenti
  - Kadang-kadang

#### 2. **STOP_REASON** - Alasan Berhenti
- **Tujuan**: Memahami mengapa customer berhenti berlangganan
- **Opsi Jawaban**:
  - Sering gangguan
  - Terlalu mahal
  - Pindah rumah
  - Pakai provider lain

#### 3. **NETWORK_ISSUES** - Masalah Jaringan
- **Tujuan**: Mengatasi keluhan teknis dan menawarkan solusi
- **Opsi Jawaban**:
  - Sudah dicek
  - Belum pernah
  - Masih bermasalah
  - Sudah diperbaiki

#### 4. **PROMO_OFFER** - Penawaran Promo
- **Tujuan**: Menawarkan promo khusus untuk customer
- **Opsi Jawaban**:
  - Tertarik
  - Tidak tertarik
  - Mau tahu detailnya
  - Pertimbangkan

#### 5. **INTEREST_CONFIRMATION** - Konfirmasi Minat
- **Tujuan**: Mengkonfirmasi minat dan proses selanjutnya
- **Opsi Jawaban**:
  - Hari ini
  - Besok
  - Minggu ini
  - Bulan depan

### 🔄 Flow Logic

Alur percakapan mengikuti diagram dengan branching logic:

```
START → SERVICE_STATUS
├─ Masih pakai → (skip ke PROMO_OFFER)
└─ Sudah berhenti → STOP_REASON
   ├─ Sering gangguan → NETWORK_ISSUES
   │  ├─ Sudah diperbaiki → PROMO_OFFER
   │  └─ Masih bermasalah → (technical follow-up)
   ├─ Terlalu mahal → PROMO_OFFER
   └─ Alasan lain → PROMO_OFFER
      └─ Tertarik → INTEREST_CONFIRMATION
```

### 📝 Questions Dataset

Setiap goal memiliki minimal 2 variasi pertanyaan dalam `WINBACK_QUESTIONS`:

- **service_status**: 2 pertanyaan untuk mengecek status
- **stop_reason**: 2 pertanyaan untuk menggali alasan
- **network_issues**: 2 pertanyaan untuk handle masalah teknis
- **promo_offer**: 2 pertanyaan untuk menawarkan promo
- **interest_confirmation**: 2 pertanyaan untuk konfirmasi

### 🛠️ Functions Available

1. **`generate_winback_question(goal, conversation_context)`**
   - Generate pertanyaan berdasarkan goal tertentu
   - Menggunakan context percakapan untuk personalisasi

2. **`get_question_from_dataset(mode="winback")`**
   - Ambil pertanyaan dari CS_DATASET untuk mode winback
   - Compatible dengan existing conversation flow

### ✅ Testing Results

Semua test berhasil:
- ✅ Goals structure sesuai diagram
- ✅ WINBACK_QUESTIONS tersedia lengkap
- ✅ generate_winback_question berfungsi
- ✅ Integration dengan existing system
- ✅ Flow scenarios sesuai diagram

### 🚀 Implementation Status

**COMPLETED:**
- [x] Update CONVERSATION_GOALS untuk winback
- [x] Implement WINBACK_QUESTIONS dataset
- [x] Create generate_winback_question function
- [x] Update CS_DATASET compatibility
- [x] Test all functions and flow scenarios

**READY FOR PRODUCTION:**
Implementasi winback goals berdasarkan flow diagram telah selesai dan siap digunakan!

### 📞 Usage Example

```python
# Get first winback question
question = generate_winback_question("service_status", {})
print(question["question"])
# Output: "Halo! Saya dari ICONNET. Apakah Bapak/Ibu saat ini masih menggunakan layanan ICONNET?"

# Progress through conversation
if customer_answer == "Sudah berhenti":
    next_question = generate_winback_question("stop_reason", {})
    
if customer_answer == "Sering gangguan":
    next_question = generate_winback_question("network_issues", {})
```