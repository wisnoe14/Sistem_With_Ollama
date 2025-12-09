# 🎯 WINBACK PREDICTION SYSTEM - FRONTEND FIELDS

## ✅ FIXED ISSUES
1. **Error `cannot access local variable 'now'`** - RESOLVED ✅
2. **Missing winback-specific fields** - ADDED ✅
3. **Frontend format compatibility** - ENHANCED ✅

## 📊 WINBACK PREDICTION FIELDS FOR FRONTEND

### 🔑 CORE PREDICTION FIELDS
| Field Name | Type | Description | Example Values |
|------------|------|-------------|----------------|
| `customer_id` | String | ID Customer | "ICON12345" |
| `topic` | String | Topic conversation | "winback" |
| `status_dihubungi` | String | Status kontak customer | "BERHASIL", "TIDAK TERHUBUNG" |
| `status` | String | Status utama | "TERTARIK REAKTIVASI", "TIDAK TERTARIK" |
| `keputusan` | String | Keputusan final | "BERHASIL REAKTIVASI", "PERLU FOLLOW-UP" |
| `probability` | String | Probabilitas sukses | "82.0%" |
| `confidence` | String | Level kepercayaan | "TINGGI", "SEDANG", "RENDAH" |
| `alasan` | String | Alasan prediksi | "Customer menunjukkan minat dan komitmen" |

### 🎯 WINBACK-SPECIFIC FIELDS
| Field Name | Type | Description | Example Values |
|------------|------|-------------|----------------|
| `minat_berlangganan` | String | Level minat reaktivasi | "Tinggi", "Sedang", "Rendah" |
| `jenis_promo` | String | Jenis promo yang ditawarkan | "Promo Reaktivasi 1 Bulan Gratis" |
| `estimasi_pembayaran` | String | Estimasi waktu aktivasi | "Target Aktivasi: Hari Ini (19 Oct 2025)" |
| `equipment_status` | String | Status perangkat customer | "Tersedia", "Sudah Dikembalikan", "Bermasalah" |
| `service_issues` | String | Riwayat masalah layanan | "Normal", "Ada Keluhan Sebelumnya" |

### 📈 ENHANCED ANALYSIS FIELDS
| Field Name | Type | Description | Example Values |
|------------|------|-------------|----------------|
| `probability_score` | Number | Skor probabilitas numerik | 82.0 |
| `confidence_level` | String | Level kepercayaan detail | "TINGGI" |
| `tanggal_prediksi` | String | Tanggal prediksi dibuat | "Sunday, 19 October 2025" |

## 🎯 DECISION CATEGORIES

### ✅ POSITIVE OUTCOMES
1. **BERHASIL REAKTIVASI** (88-95% probability)
   - Customer setuju reaktivasi dengan commitment jelas
   - Equipment tersedia
   - Timeline pembayaran jelas

2. **TERTARIK REAKTIVASI** (75-90% probability) 
   - Customer menunjukkan minat tinggi
   - Ada komitmen untuk reaktivasi
   - Minimal objection

### 📊 MODERATE OUTCOMES
3. **KEMUNGKINAN TERTARIK** (55-75% probability)
   - Ada ketertarikan tapi masih ragu
   - Objection minimal
   - Perlu pendekatan lanjutan

4. **PERLU FOLLOW-UP** (40-60% probability)
   - Respon dalam tahap evaluasi
   - Butuh pendekatan khusus
   - Timeline belum pasti

### ❌ NEGATIVE OUTCOMES  
5. **TIDAK TERTARIK** (15-35% probability)
   - Resistensi kuat dari customer
   - Banyak objection
   - Price sensitivity tinggi

## 🔄 TIMELINE ANALYSIS

### 📅 ACTIVATION TIMELINE DETECTION
System secara otomatis mendeteksi komitmen waktu dari percakapan:

- **"hari ini"** → Target Aktivasi: Hari Ini
- **"besok"** → Target Aktivasi: Besok  
- **"1-2 jam"** → Target Aktivasi: Hari Ini
- **No specific time** → Target Aktivasi: +3 hari

### 🛠️ EQUIPMENT STATUS DETECTION
- **"masih ada"**, **"normal"** → Equipment Status: "Tersedia"
- **"sudah dikembalikan"** → Equipment Status: "Sudah Dikembalikan"
- **"hilang"**, **"rusak"** → Equipment Status: "Bermasalah"

### ⚠️ SERVICE ISSUE DETECTION
- **"gangguan"**, **"putus"**, **"lambat"**, **"keluhan"** → Service Issues: "Ada Keluhan Sebelumnya"
- Default → Service Issues: "Normal"

## 🎯 FRONTEND INTEGRATION EXAMPLE

```javascript
// Frontend dapat menggunakan fields ini untuk dashboard:
const winbackResult = {
  customer_id: "ICON12345",
  topic: "winback", 
  keputusan: "TERTARIK REAKTIVASI",
  probability: "82.0%",
  confidence: "TINGGI",
  minat_berlangganan: "Tinggi",
  jenis_promo: "Promo Reaktivasi 1 Bulan Gratis", 
  estimasi_pembayaran: "Target Aktivasi: Hari Ini (19 Oct 2025)",
  equipment_status: "Tersedia",
  service_issues: "Normal"
};

// Dashboard dapat menampilkan:
// - Badge: "TERTARIK REAKTIVASI" (82% - TINGGI)
// - Promo: "Promo Reaktivasi 1 Bulan Gratis"
// - Timeline: "Target Aktivasi: Hari Ini"
// - Equipment: "Tersedia" ✅
// - Service: "Normal" ✅
```

## 🚀 API ENDPOINT
```
POST /api/v1/endpoints/conversation/predict
```

## 📝 SAMPLE RESPONSE
```json
{
  "result": {
    "customer_id": "ICON12345",
    "mode": "winback",
    "topic": "winback",
    "status_dihubungi": "BERHASIL",
    "status": "TERTARIK REAKTIVASI",
    "keputusan": "TERTARIK REAKTIVASI", 
    "probability": "82.0%",
    "confidence": "TINGGI",
    "alasan": "Customer menunjukkan minat dan komitmen untuk reaktivasi",
    "minat_berlangganan": "Tinggi",
    "jenis_promo": "Promo Reaktivasi 1 Bulan Gratis",
    "estimasi_pembayaran": "Target Aktivasi: Hari Ini (19 October 2025)",
    "equipment_status": "Tersedia", 
    "service_issues": "Normal",
    "probability_score": 82.0,
    "confidence_level": "TINGGI",
    "tanggal_prediksi": "Sunday, 19 October 2025"
  }
}
```

## 🎯 KEY BENEFITS FOR FRONTEND

1. **📊 Rich Data**: Comprehensive fields for detailed dashboard
2. **🎯 Actionable**: Clear next steps and timelines
3. **📈 Categorized**: Easy to create badges and status indicators
4. **🔍 Detailed**: Equipment and service status for context
5. **⏰ Time-aware**: Specific activation timelines and dates

---
*✅ Sistem prediksi winback sekarang sudah fully compatible dengan kebutuhan frontend!*