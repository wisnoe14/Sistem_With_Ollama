from backend.app.services.gpt_service import generate_question


def run():
    conv = []

    # 0) Opening greeting
    conv.append({
        "question": "Selamat siang, Bapak/Ibu. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Budi?",
        "answer": "Ya, benar"
    })
    print("STEP 0 NEXT:", generate_question('winback', conv)['question'])

    # 1) service_status → Ada gangguan
    conv.append({
        "question": "Baik Bapak/Ibu, bagaimana kondisi layanan ICONNET saat ini? Apakah ada kendala?",
        "answer": "Ada gangguan"
    })
    print("STEP 1 NEXT:", generate_question('winback', conv)['question'])

    # 2) complaint_apology → Belum pernah
    conv.append({
        "question": "Mohon maaf sebelumnya atas ketidaknyamanan yang Bapak/Ibu alami. Apakah sudah pernah melaporkan gangguan ini?",
        "answer": "Belum pernah"
    })
    print("STEP 2 NEXT:", generate_question('winback', conv)['question'])

    # 3) complaint_resolution (detail kendala) → Lambat
    conv.append({
        "question": "Baik Bapak/Ibu, agar kami bisa bantu, mohon jelaskan detail kendala yang dirasakan (misal lampu LOS, koneksi putus, lambat).",
        "answer": "Lambat"
    })
    print("STEP 3 NEXT:", generate_question('winback', conv)['question'])

    # 4) program_confirmation → Ya, bersedia
    conv.append({
        "question": "Sebagai tindak lanjut, apakah Bapak/Ibu bersedia melanjutkan layanan dengan program solusi yang kami tawarkan?",
        "answer": "Ya, bersedia"
    })
    print("STEP 4 NEXT:", generate_question('winback', conv)['question'])


if __name__ == "__main__":
    run()
