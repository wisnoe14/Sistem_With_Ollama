import hashlib
import os
import json
import re
import requests
from typing import Union


def truncate_to_n_words(text, n=7):
    """Potong teks maksimal n kata."""
    return " ".join(text.split()[:n])


# Cache dictionary untuk response Ollama
_ollama_cache = {}


def cache_key(*args, **kwargs):
    key_str = str(args) + str(kwargs)
    return hashlib.md5(key_str.encode()).hexdigest()


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")


def predict_status_promo_ollama(answers: list) -> dict:
    """
    Prediksi status, promo, estimasi bayar, alasan menggunakan Ollama.
    """
    percakapan = " | ".join([str(a) for a in answers if a])
    prompt = (
        f"Berdasarkan percakapan berikut: {percakapan}. "
        "Prediksikan status pelanggan (pilihan: Pelanggan tidak dapat dihubungi, Closing, Pelanggan dapat dihubungi, Bersedia Membayar) "
        "dan jenis promo yang sesuai (pilihan: Tidak Ada Promo, Promo Diskon, Promo Cashback, Promo Gratis Bulan, Promo Lainnya). "
        "Format output: Status: <status>, Promo: <jenis_promo>, Estimasi Pembayaran: <estimasi jika ada, jika tidak tulis 'Belum tersedia'>, Alasan: <ringkas alasan dari jawaban>. Jawab maksimal 7 kata per field."
    )
    key = cache_key(prompt, "predict_status_promo_ollama")
    if key in _ollama_cache:
        content = _ollama_cache[key]
    else:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        try:
            resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("response", "")
        except Exception:
            content = ""
        _ollama_cache[key] = content
    # Parsing output sederhana
    result = {}
    for line in content.split(','):
        if ':' in line:
            k, v = line.split(':', 1)
            result[k.strip().lower().replace(' ', '_')] = v.strip()
    # Standarisasi key
    return {
        "status": result.get("status", ""),
        "promo": result.get("promo", ""),
        "estimasi_bayar": result.get("estimasi_pembayaran", ""),
        "alasan": result.get("alasan", "")
    }




def generate_question(topic: str, context: Union[str, list] = "") -> dict:
    """
    Generate pertanyaan + opsi jawaban dari context percakapan.
    """
    percakapan = ""
    if isinstance(context, list):
        percakapan = " | ".join([f"Q:{c.get('q','')} A:{c.get('a','')}" for c in context if isinstance(c, dict) and c.get('a', '').strip()])
    elif isinstance(context, str):
        percakapan = context

    # Fallback: jika context hanya status dihubungi, berikan pertanyaan default
    if isinstance(context, list) and len(context) == 1 and context[0].get('q', '').lower().strip() == 'status dihubungi?' and context[0].get('a', '').strip().lower() == 'bisa dihubungi':
        # Default question per topic
        if topic == 'winback':
            q = "Selamat Pagi/Siang/Sore Perkenalkan Saya (Nama Agen) Dari ICONNET, Apakah Benar Saya Terhubung Dengan (Nama Pelanggan) ?, Baik Bapak/Ibu. Kami Melihat Bahwa Layanan ICONNET Bapak/Ibu Sedang Terputus dan Kami Ingin Tahu Apakah Ada Kendala Yang Bisa Kami Bantu?"
            opts = ["Butuh layanan", "Promo menarik", "Pelayanan lebih baik", "Lainnya"]
        elif topic == 'retention':
            q = "Selamat Pagi/Siang/Sore Perkenalkan Saya (Nama Agen) Dari ICONNET, Apakah Benar Saya Terhubung Dengan (Nama Pelanggan) ?, Baik Bapak/Ibu. Kami Melihat Bahwa Layanan ICONNET Bapak/Ibu Sedang Terputus dan Kami Ingin Tahu Apakah Ada Kendala Yang Bisa Kami Bantu?"
            opts = ["Tagihan", "Teknis", "Layanan", "Lainnya"]
        else:
            q = "Selamat Pagi/Siang/Sore Perkenalkan Saya (Nama Agen) Dari ICONNET, Apakah Benar Saya Terhubung Dengan (Nama Pelanggan) ?, Baik Bapak/Ibu. Kami Melihat Bahwa Layanan ICONNET Bapak/Ibu Sedang Terputus dan Kami Ingin Tahu Apakah Ada Kendala Yang Bisa Kami Bantu?"
            opts = ["Belum gajian", "Lupa bayar", "Tagihan tinggi", "Lainnya"]
        return {"question": q, "options": opts}

    prompt = (
        f"Mode: {topic}. Percakapan: {percakapan}. "
        "Buat 1 pertanyaan singkat dengan 4 opsi jawaban. "
        "Format JSON: {\"question\": \"...\", \"options\": [\"...\",\"...\",\"...\",\"...\"]}. "
        "Jawab maksimal 7 kata per field."
    )

    print("[DEBUG PROMPT]", prompt)

    key = cache_key(prompt, "generate_question_ollama")
    if key in _ollama_cache:
        result_json = _ollama_cache[key]
    else:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        try:
            resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            result_json = data.get("response", "")
        except Exception:
            result_json = ""
        _ollama_cache[key] = result_json

    print("[DEBUG OLLAMA RAW OUTPUT]", result_json)

    # Robust JSON parsing (regex)
    try:
        match = re.search(r"\{.*\}", result_json, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
        else:
            data = {}
        q = truncate_to_n_words(data.get("question", ""), 7)
        opts = [truncate_to_n_words(o, 7) for o in data.get("options", []) if isinstance(o, str) and o.strip()]
        # Fallback jika parsing sukses tapi kosong
        if not q or not opts:
            return {"question": "Pertanyaan tidak tersedia", "options": ["Jawaban 1", "Jawaban 2", "Jawaban 3", "Jawaban 4"]}
        return {"question": q, "options": opts}
    except Exception as e:
        print("[DEBUG PARSE ERROR]", e)
        return {"question": "Pertanyaan tidak tersedia", "options": ["Jawaban 1", "Jawaban 2", "Jawaban 3", "Jawaban 4"]}


# Tidak dipakai, hapus process_customer_answer


def save_conversation_to_excel(
    customer_id: str,
    mode: str,
    status_dihubungi: str,
    percakapan: list,
    prediction: dict = None,
    filename: str = "riwayat_simulasi_cs.xlsx"
) -> str:
    """
    Simpan riwayat percakapan ke file Excel (openpyxl).
    Kolom: customer_id, mode, status_dihubungi, pertanyaan, jawaban, prediksi_status, promo, estimasi_bayar, alasan, timestamp
    """
    from openpyxl import Workbook, load_workbook
    import datetime
    if prediction is None:
        # Otomatis prediksi jika belum ada
        answers = [item.get("a", "") for item in percakapan if item.get("a", "")]
        prediction = predict_status_promo_ollama(answers)
    pred_status = prediction.get("status", "")
    promo = prediction.get("promo", "")
    estimasi_bayar = prediction.get("estimasi_bayar", "")
    alasan = prediction.get("alasan", "")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Cek apakah file sudah ada
    if os.path.exists(filename):
        wb = load_workbook(filename)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.append([
            "customer_id", "mode", "status_dihubungi", "pertanyaan", "jawaban", "prediksi_status", "promo", "estimasi_bayar", "alasan", "timestamp"
        ])
    # Simpan setiap step percakapan
    for step in percakapan:
        pertanyaan = step.get("q", "")
        jawaban = step.get("a", "")
        ws.append([
            customer_id,
            mode,
            status_dihubungi,
            pertanyaan,
            jawaban,
            pred_status,
            promo,
            estimasi_bayar,
            alasan,
            timestamp
        ])
    wb.save(filename)
    return filename
