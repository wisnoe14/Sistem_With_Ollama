# 📚 ICONNET Retention Knowledge Base

Training knowledge untuk Customer Service Retention ICONNET yang digunakan pada model Llama3/Ollama.

## 📁 Files

- **`retention-knowledge.txt`** - Knowledge base lengkap untuk retention CS
- **`Modelfile-retention`** - Ollama modelfile untuk build custom retention model

## 🚀 Quick Start

### 1️⃣ Build Retention Model (Optional)

Jika ingin membuat custom Ollama model khusus retention:

```bash
ollama create retention-cs -f Modelfile-retention
```

### 2️⃣ Test Model

```bash
ollama run retention-cs
```

### 3️⃣ Contoh Prompt Test

**Test 1 - Pindah Rumah:**
```
User: Saya pindah rumah jadi berhenti dulu
```

Expected Response:
```
Baik Bapak/Ibu, terima kasih informasinya. Untuk lokasi rumah baru Bapak/Ibu saat ini, 
apakah sudah ada coverage layanan ICONNET? Jika sudah, apakah Bapak/Ibu berminat untuk 
memasang kembali layanan ICONNET di lokasi baru?
```

**Test 2 - Keluhan Gangguan:**
```
User: Internetnya sering lambat dan putus-putus
```

Expected Response:
```
Mohon maaf sebelumnya atas kendala yang Bapak/Ibu alami. Apakah sebelumnya sudah pernah 
membuat laporan gangguan ke tim support kami? Kami akan bantu koordinasikan pengecekan 
ulang dengan tim teknis. Jika kendala dapat teratasi, apakah Bapak/Ibu bersedia untuk 
melanjutkan layanan?
```

**Test 3 - Pertimbangkan:**
```
User: Saya mau pikir-pikir dulu
```

Expected Response:
```
Baik Bapak/Ibu, tidak masalah. Kira-kira kapan Bapak/Ibu dapat memutuskan? 
Kami akan follow-up kembali sesuai waktu yang Bapak/Ibu tentukan.
```

**Test 4 - Setuju Lanjut:**
```
User: Iya mau lanjut, promonya menarik
```

Expected Response:
```
Baik Bapak/Ibu, terima kasih atas keputusannya. Kami akan segera mengirimkan kode 
pembayaran ke email Bapak/Ibu yang terdaftar. Untuk estimasi, kapan pembayaran dapat 
dilakukan dari sekarang?
```

## 🎯 Integration dengan Backend

Knowledge base retention sudah terintegrasi di:
```
backend/app/services/gpt_service.py
```

Fungsi `generate_dynamic_question_with_llama3()` akan menggunakan `retention_knowledge` 
ketika `mode="retention"`.

## 📊 Retention Goals Flow

```
1. greeting_identity → Verifikasi pelanggan
2. wrong_number_check → Cek jika bukan pemilik
3. service_check → Cek status layanan terputus
4. promo_permission → Minta izin sampaikan promo
5. promo_detail → Jelaskan diskon 20%/25%/30%
6. activation_interest → Tanya minat aktivasi
   ├─ YA → payment_confirmation → payment_timing → closing
   ├─ TIDAK → rejection_reason
   │   ├─ Pindah → device_location → relocation_interest → closing
   │   ├─ Keluhan → complaint_handling → complaint_resolution → closing
   │   └─ Lainnya → device_location → closing
   ├─ PERTIMBANGKAN → consideration_timeline → closing
   └─ BERHENTI → stop_confirmation → closing
```

## 🔧 Promo Retention Official

```
✅ Diskon 20% - Berlangganan bulanan
✅ Diskon 25% - Paket 6 bulan
✅ Diskon 30% - Paket 12 bulan
```

## 📝 Tone & Style Guidelines

✅ **WAJIB:**
- Sopan, ramah, tidak memaksa
- Dengarkan dengan empati
- Fokus pada solusi untuk pelanggan
- Hormati keputusan akhir

❌ **HINDARI:**
- Tone jualan keras/agresif
- Mengabaikan keluhan pelanggan
- Memaksa pelanggan untuk lanjut
- Keluar dari konteks retention ICONNET

## 🧪 Testing

Untuk test retention flow lengkap, gunakan:
```bash
python test_retention_flow.py
```

Atau test via API:
```bash
curl -X POST http://localhost:8000/api/v1/endpoints/conversation/cs-chatbot/start \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "ICON12345",
    "customer_name": "Budi",
    "cs_name": "Wisnu",
    "mode": "retention",
    "time_of_day": "siang"
  }'
```

## 📚 Related Files

- **Winback Knowledge:** `winback-knowledge.txt`, `Modelfile-winback`
- **Telecollection:** (integrated in `gpt_service.py`)
- **Main Service:** `backend/app/services/gpt_service.py`

## 🆘 Troubleshooting

**Q: Model tidak generate sesuai knowledge?**
A: Pastikan temperature tidak terlalu tinggi (gunakan 0.3-0.4), dan num_ctx cukup besar (2048+).

**Q: Response terlalu generic?**
A: Tambahkan few-shot examples di prompt atau tuning ulang parameter repeat_penalty.

**Q: Keluar dari konteks retention?**
A: Perkuat system prompt dan tambahkan guardrails di code untuk validasi response.

---

✅ **Knowledge Base Ready!**  
Retention mode sekarang memiliki training knowledge yang lengkap seperti Winback.
