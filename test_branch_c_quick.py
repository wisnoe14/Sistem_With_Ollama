from backend.app.services.gpt_service import generate_question

# Branch C quick simulation: Tidak ada gangguan -> payment_status_info -> payment_timing -> program_confirmation -> closing
conv = []
conv.append({"question":"Selamat siang, Bapak/Ibu. Perkenalkan saya Wisnu dari ICONNET. Apakah benar saya terhubung dengan Bapak/Ibu Budi?","answer":"Ya, benar"})
print('NEXT0:', generate_question('winback', conv)['goal'])
conv.append({"question":"Baik Bapak/Ibu, bagaimana kondisi layanan ICONNET saat ini? Apakah ada kendala?","answer":"Tidak ada gangguan"})
q1 = generate_question('winback', conv)
print('NEXT1:', q1['goal'], '-', q1['question'][:80])
conv.append({"question": q1['question'], "answer":"Ada"})
q2 = generate_question('winback', conv)
print('NEXT2:', q2['goal'], '-', q2['question'][:80])
conv.append({"question": q2['question'], "answer":"Besok"})
q3 = generate_question('winback', conv)
print('NEXT3:', q3['goal'], '-', q3['question'][:80])
