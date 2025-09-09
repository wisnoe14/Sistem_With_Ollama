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



OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Cek dan pull model jika belum ada
import subprocess
import requests as reqs
def ensure_ollama_model(model_name: str):
    try:
        resp = reqs.get("http://localhost:11434/api/tags")
        if resp.status_code == 200:
            tags = resp.json().get("models", [])
            if not any(m.get("name", "").startswith(model_name) for m in tags):
                print(f"[INFO] Model {model_name} belum ada, melakukan pull...")
                subprocess.run(["ollama", "pull", model_name], check=True)
    except Exception as e:
        print(f"[WARNING] Tidak bisa cek/pull model Ollama: {e}")

ensure_ollama_model(OLLAMA_MODEL)



def predict_status_promo_ollama(answers: list) -> dict:
    """
    Prediksi status, promo, estimasi bayar, alasan menggunakan Ollama (via /api/chat).
    """
    percakapan = " | ".join([str(a) for a in answers if a])
    prompt = (
        f"Percakapan: {percakapan}. Prediksi status (Pelanggan tidak dapat dihubungi, Closing, Pelanggan dapat dihubungi, Bersedia Membayar) dan promo (Tidak Ada Promo, Promo Diskon, Promo Cashback, Promo Gratis Bulan, Promo Lainnya). Format: Status: <status>, Promo: <jenis_promo>, Estimasi: <estimasi atau 'Belum tersedia'>, Alasan: <alasan ringkas, max 7 kata>."
    )
    key = cache_key(prompt, "predict_status_promo_ollama_chat")
    if key in _ollama_cache:
        content = _ollama_cache[key]
    else:
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": "Kamu adalah asisten customer service yang membantu memprediksi status dan promo pelanggan."},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        try:
            resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            # /api/chat returns 'message' with 'content'
            content = data.get("message", {}).get("content", "")
        except Exception as e:
            print(f"[OLLAMA ERROR][predict_status_promo_ollama] {e}")
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
    Generate pertanyaan + opsi jawaban dari context percakapan (via /api/chat).
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

    # Ambil jawaban terakhir user jika ada
    last_answer = ""
    if isinstance(context, list) and len(context) > 1:
        last_answer = context[-1].get('a', '')

    prompt = (
        f"Mode: {topic}. Percakapan: {percakapan}. Jawaban terakhir: {last_answer}. Buat 1 pertanyaan CS singkat (max 20 kata, relevan, tidak duplikat) dan 4 opsi jawaban (max 7 kata/opsi). Format: {{\"question\":\"...\", \"options\":[\"...\",\"...\",\"...\",\"...\"]}}. Tanpa penjelasan lain."
    )

    print("[DEBUG PROMPT]", prompt)

    key = cache_key(prompt, "generate_question_ollama_chat")
    if key in _ollama_cache:
        result_json = _ollama_cache[key]
    else:
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": "Kamu adalah asisten customer service yang membantu membuat pertanyaan dan opsi jawaban."},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        try:
            resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            # /api/chat returns 'message' with 'content'
            result_json = data.get("message", {}).get("content", "")
        except Exception as e:
            print(f"[OLLAMA ERROR][generate_question] {e}")
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
