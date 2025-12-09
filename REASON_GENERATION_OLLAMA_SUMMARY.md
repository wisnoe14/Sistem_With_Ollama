# Summary: Reason Generation dengan Ollama

## 📋 Overview
Implementasi sistem generate alasan prediksi yang naratif dan koheren menggunakan Ollama LLM, menggantikan template hardcoded yang mengandung persentase.

## ✅ Perubahan yang Dilakukan

### 1. Fungsi Baru: `generate_reason_with_ollama()`
**File**: `backend/app/services/gpt_service.py`

Fungsi utama untuk generate alasan menggunakan Ollama dengan fallback mechanism:

```python
def generate_reason_with_ollama(
    conversation_history: List[Dict], 
    mode: str, 
    keputusan: str, 
    analysis_data: Dict
) -> str
```

**Fitur**:
- ✅ Generate alasan naratif 2-3 kalimat
- ✅ Tidak menggunakan persentase atau angka teknis
- ✅ Fokus pada pola jawaban customer
- ✅ Context-aware berdasarkan mode (telecollection/winback/retention)
- ✅ Automatic fallback jika Ollama gagal/timeout

**Prompt Design**:
- Merangkum 5 percakapan terakhir untuk context
- Menyertakan data analisis (tanpa menampilkan ke output)
- Instruksi eksplisit: "Jangan gunakan persentase atau angka-angka"
- Format output: Bahasa Indonesia formal, naratif natural

### 2. Fungsi Fallback: `_generate_fallback_reason()`
**File**: `backend/app/services/gpt_service.py`

Fallback function yang generate alasan template-based jika Ollama gagal:

```python
def _generate_fallback_reason(
    conversation_history: List[Dict], 
    mode: str, 
    keputusan: str, 
    analysis_data: Dict
) -> str
```

**Kapan digunakan**:
- Ollama tidak tersedia
- Ollama timeout (>15 detik)
- Ollama error/crash
- Response terlalu pendek (<50 chars) atau terlalu panjang (>500 chars)

### 3. Update Prediction Functions

#### `predict_telecollection_outcome()`
Semua 6 return statement di-update untuk menggunakan `generate_reason_with_ollama()`:

1. **SUDAH BAYAR** (payment completed)
2. **KEMUNGKINAN BAYAR** (moderate commitment)
3. **BELUM PASTI** (high barriers + cooperation)
4. **SULIT BAYAR** (high barriers)
5. **KEMUNGKINAN BAYAR** (positive sentiment)
6. **BELUM PASTI** (neutral/unclear)

#### `predict_winback_outcome()`
Semua keputusan di-update untuk menggunakan `generate_reason_with_ollama()`:

1. **BERHASIL REAKTIVASI**
2. **TERTARIK REAKTIVASI**
3. **KEMUNGKINAN TERTARIK**
4. **TIDAK TERTARIK**
5. **PERLU FOLLOW-UP**

## 📊 Hasil Testing

### Test Results:
✅ **Telecollection** - 2 test cases passed
- Case 1: Komitmen timeline kuat
- Case 2: Kendala berat

✅ **Winback** - 2 test cases passed
- Case 1: Customer tertarik reaktivasi
- Case 2: Customer tidak tertarik

✅ **Retention** - 1 test case passed
- Case 1: Customer mau lanjut berlangganan

### Validasi:
✅ Semua alasan tidak mengandung persentase (%)
✅ Panjang alasan > 50 karakter (informative)
✅ Alasan koheren dan naratif
✅ Fallback mechanism berfungsi dengan baik

## 🎯 Contoh Output

### Sebelum (Dengan Persentase):
```
"Customer menghadapi kendala signifikan (87.5%) namun menunjukkan 
sikap kooperatif (52.5%) dalam berkomunikasi. Kendala utama: 
'Belum gajian, lagi susah uang'. Masih ada potensi pembayaran 
dengan pendekatan yang tepat."
```

### Sesudah (Naratif Tanpa Persentase):
```
"Customer menghadapi kendala yang cukup signifikan dalam melakukan 
pembayaran. Diperlukan pendekatan khusus dan mungkin solusi 
alternatif seperti penjadwalan ulang atau restrukturisasi untuk 
memfasilitasi penyelesaian tagihan."
```

## 🔧 Konfigurasi Ollama

### Model: llama3
### Timeout: 15 detik
### Parameters:
```python
{
    "temperature": 0.7,
    "num_predict": 150,
    "num_ctx": 1024,
    "top_p": 0.9
}
```

## 📝 Mode Support

| Mode | Support | Test Status |
|------|---------|-------------|
| Telecollection | ✅ | Passed |
| Winback | ✅ | Passed |
| Retention | ✅ | Passed |

## 🚀 Keunggulan Implementasi

1. **Lebih Natural**: Alasan berbentuk narasi koheren, bukan bullet point teknis
2. **Context-Aware**: Menyesuaikan dengan mode conversation
3. **Reliable**: Fallback mechanism memastikan selalu ada output
4. **Maintainable**: Centralized logic di satu fungsi
5. **Flexible**: Mudah di-customize prompt untuk hasil yang lebih baik

## 📁 File yang Diubah

1. `backend/app/services/gpt_service.py`
   - Added: `generate_reason_with_ollama()`
   - Added: `_generate_fallback_reason()`
   - Modified: `predict_telecollection_outcome()` (6 return statements)
   - Modified: `predict_winback_outcome()` (1 decision logic)

2. `test_reason_generation.py` (NEW)
   - Test telecollection reason generation
   - Test winback reason generation
   - Test retention reason generation

## 🎓 Usage Example

```python
from app.services.gpt_service import predict_telecollection_outcome

conversation = [
    {"q": "Kapan bisa bayar?", "a": "Besok pagi", "goal": "payment_timeline"}
]

result = predict_telecollection_outcome(conversation)

# result['alasan'] akan berisi:
# "Customer menunjukkan komitmen untuk melakukan pembayaran dengan 
# memberikan timeline yang jelas. Sikap kooperatif customer dalam 
# percakapan mengindikasikan niat positif untuk menyelesaikan tagihan."
```

## ✨ Next Steps (Optional)

1. Fine-tune Ollama prompt untuk hasil lebih baik
2. Add caching untuk reason yang sama
3. Implement A/B testing untuk compare quality
4. Add sentiment analysis pada reason output
5. Monitor Ollama performance dan optimize timeout

---

**Status**: ✅ COMPLETED & TESTED
**Author**: Wisnu
**Date**: November 1, 2025
