# 📞 ALUR WINBACK ICONNET - Dokumentasi

## 🎯 Overview
Sistem winback telah diimplementasikan dengan branching logic yang mengikuti flow Customer Service ICONNET untuk mengembalikan pelanggan yang layanannya terputus.

## 🔄 Flow Lengkap Winback

### 1. **GREETING & KONFIRMASI NAMA**
```
CS: "Selamat pagi/siang/sore, Bapak/Ibu. Perkenalkan saya Aisyah dari ICONNET. 
     Apakah benar saya terhubung dengan Bapak/Ibu [Nama Pelanggan]?"

Opsi Response:
- Ya, benar
- Bukan, salah sambung  
- Saya keluarganya
- Siapa yang dicari?
```

### 2. **BRANCHING - KONFIRMASI IDENTITAS**

#### 2A. **Jika PEMILIK LANGSUNG (Ya, benar)**
```
CS: "Terima kasih, Bapak/Ibu. Kami melihat bahwa layanan ICONNET Bapak/Ibu sedang terputus, 
     dan kami ingin tahu apakah ada kendala yang bisa kami bantu? 
     Saat ini kami sedang memiliki promo menarik untuk Bapak/Ibu. 
     Apakah boleh saya sampaikan lebih lanjut?"

Opsi Response:
- Boleh, sampaikan
- Tidak tertarik
- Ada kendala teknis
- Sudah pindah rumah
```

#### 2B. **Jika BUKAN PEMILIK**
```
CS: "Mohon maaf, Bapak/Ibu. Di data kami, layanan ini terdaftar atas nama pelanggan ICONNET. 
     Apakah saya dapat mengetahui apakah Bapak/Ibu adalah pemilik atau pengguna layanan tersebut?"

Opsi Response:
- Saya pemiliknya
- Saya keluarga pemilik
- Bukan, salah nomor
- Pemilik tidak ada
```

##### 2B1. **Jika KELUARGA PEMILIK**
```
CS: "Baik Bapak/Ibu, sebagai keluarga pemilik, kami ingin menginformasikan bahwa layanan ICONNET sedang terputus. 
     Kami memiliki promo menarik untuk mengaktifkan kembali. Apakah boleh saya sampaikan?"

Opsi Response:
- Boleh, sampaikan
- Harus izin pemilik dulu
- Tidak tertarik
- Nanti pemilik yang putuskan
```

##### 2B2. **Jika PEMILIK TIDAK ADA**
```
CS: "Mohon dibantu menginformasikan nomor telepon pemilik layanan 
     agar kami dapat menghubungi yang bersangkutan ya Bapak/Ibu"

Opsi Response:
- Akan saya berikan
- Tidak tahu nomornya
- Nanti pemilik yang hubungi
- Selesai
```

### 3. **PENAWARAN PROMO**
```
CS: "Sebagai bentuk apresiasi, kami menawarkan promo gratis 1 bulan untuk Bapak/Ibu 
     jika bersedia mengaktifkan layanan ICONNET kembali. 
     Promo ini bisa Bapak/Ibu dapatkan dengan cara melakukan 1x pembayaran untuk mengaktifkan layanan ICONNETnya. 
     Apakah Bapak/Ibu bersedia untuk mengaktifkan layanan ICONNETnya kembali?"

Opsi Response:
- Ya, bersedia
- Tidak, terima kasih
- Pertimbangkan dulu
- Ada kendala
```

### 4. **BRANCHING BERDASARKAN RESPONSE**

#### 4A. **JIKA BERSEDIA** ✅
```
CS: "Baik Bapak/Ibu, akan kami bantu untuk mengirimkan kode pembayaran melalui email. 
     Untuk estimasi pembayaran akan dibayarkan berapa jam ke depan ya?"

Opsi Response:
- 1-2 jam
- Hari ini juga
- Besok  
- Beberapa hari lagi

→ LANJUT: Konfirmasi email terkirim
```

#### 4B. **JIKA TIDAK BERSEDIA** ❌
```
CS: "Baik Bapak/Ibu, jika boleh tahu karena apa ya? 
     Apakah perangkatnya masih berada di lokasi?"

Opsi Response:
- Pindah rumah
- Ada keluhan layanan
- Tidak butuh internet
- Alasan keuangan

→ BRANCHING ke handling spesifik
```

#### 4C. **JIKA PERTIMBANGKAN** 🤔
```
CS: "Sekiranya kapan Bapak/Ibu bersedia mengonfirmasikan ya?"

Opsi Response:
- Nanti siang
- Besok
- Akhir pekan
- Masih belum pasti
```

### 5. **SUB-BRANCHING UNTUK PENOLAKAN**

#### 5A. **PINDAH RUMAH** 🏠
```
CS: "Baik Bapak/Ibu, untuk di rumah saat ini apakah sudah terpasang wifi ICONNET? 
     Jika belum, apakah Bapak/Ibu berminat untuk pasang kembali?"

Opsi Response:
- Sudah terpasang
- Belum, mau pasang
- Belum, tidak minat
- Masih pertimbangan
```

#### 5B. **ADA KELUHAN** ⚠️
```
CS: "Baik, mohon maaf atas ketidaknyamanannya, akan kami teruskan ke tim terkait ya Bapak/Ibu. 
     Apakah dengan perbaikan layanan dan promo gratis 1 bulan, Bapak/Ibu bersedia mencoba lagi?"

Opsi Response:
- Ya, mau coba lagi
- Tidak, tetap berhenti
- Tunggu perbaikan dulu
- Masih ragu
```

#### 5C. **ALASAN KEUANGAN** 💰
```
CS: "Kami memahami situasi Bapak/Ibu. Selain promo gratis 1 bulan, 
     kami juga bisa berikan diskon khusus untuk beberapa bulan ke depan. Apakah ini membantu?"

Opsi Response:
- Ya, tertarik
- Masih terlalu mahal
- Butuh info detail
- Tidak tertarik
```

### 6. **PENUTUPAN**

#### 6A. **CLOSING POSITIF** ✅
```
CS: "Baik Bapak/Ibu, email sudah kami kirimkan. Mohon cek email untuk kode pembayarannya. 
     Apakah ada hal lain yang bisa kami bantu?"

→ "Baik Bapak/Ibu, terima kasih atas waktu dan konfirmasinya, mohon maaf mengganggu. Selamat siang!"
```

#### 6B. **CLOSING NEGATIF** ❌
```
CS: "Oke baik, kami konfirmasi ulang bahwa Bapak/Ibu berhenti berlangganan ya. 
     Terima kasih atas waktunya, mohon maaf mengganggu."
```

## 🚀 Cara Menggunakan

1. **Pilih Topic "Winback"** saat mulai simulasi
2. **Sistem akan otomatis mengikuti flow** yang telah diimplementasikan
3. **Setiap response pelanggan** akan trigger pertanyaan follow-up yang sesuai
4. **Alur akan berakhir** dengan closing positif atau negatif

## 🎯 Fitur Khusus

- ✅ **Smart Branching**: Sistem mendeteksi jawaban dan mengarahkan ke flow yang tepat
- ✅ **Context Aware**: Mengingat percakapan sebelumnya untuk pertanyaan yang relevan  
- ✅ **Multiple Scenarios**: Handle pemilik langsung, keluarga, salah sambung
- ✅ **Professional Tone**: Menggunakan bahasa CS yang sopan and emphatik
- ✅ **Complete Flow**: Dari greeting hingga closing sesuai SOP ICONNET

## 📊 Tracking & Analytics

Sistem akan menyimpan:
- ✅ **Status akhir**: Reaktivasi, Berhenti, Pertimbangan
- ✅ **Alasan**: Pindah rumah, Keluhan, Keuangan, dll
- ✅ **Timeline**: Estimasi pembayaran (khusus untuk yang bersedia)
- ✅ **Export**: Data bisa diekspor ke Excel untuk reporting

---

**🎉 Alur Winback siap digunakan! Sistem akan otomatis mengikuti flow yang telah diimplementasikan sesuai SOP ICONNET.**