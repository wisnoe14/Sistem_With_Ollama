from backend.app.services.gpt_service import generate_question

def _append(conv, qdict, answer_text):
    conv.append({
        "question": qdict.get('question'),
        "goal": qdict.get('goal'),
        "answer": answer_text,
    })

conv = []
conv.append({"question": "Halo", "answer": "Ya, benar"})
print('After initial:', conv)
q0 = generate_question('retention', conv)
print('q0 goal:', q0.get('goal'))
_append(conv, q0, "Ya, terputus")
print('After q0 append:', conv)
q1 = generate_question('retention', conv)
print('q1 goal:', q1.get('goal'))
_append(conv, q1, "Boleh")
print('After q1 append:', conv)
q2 = generate_question('retention', conv)
print('q2 goal:', q2.get('goal'))
_append(conv, q2, "Oke")
print('After q2 append:', conv)
q3 = generate_question('retention', conv)
print('q3 goal:', q3.get('goal'))
_append(conv, q3, "Berhenti")
print('After q3 append:', conv)
q4 = generate_question('retention', conv)
print('q4 goal:', q4.get('goal'))
_append(conv, q4, "Ya, yakin")
print('After q4 append:', conv)
q5 = generate_question('retention', conv)
print('q5 goal:', q5.get('goal'), 'is_closing:', q5.get('is_closing'))
print('\nFull conversation:')
for i,c in enumerate(conv):
    print(i, c)
