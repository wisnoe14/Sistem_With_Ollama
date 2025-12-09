import requests

BASE_URL = "http://localhost:8000/api/v1/endpoints/conversation"

conv = []
print("== Test Winback Branch A (sudah berhenti) ==")
# Q1 greeting
r = requests.post(f"{BASE_URL}/generate-simulation-questions", json={"customer_id":"TA","topic":"winback","conversation":conv})
res = r.json()
print("Q1:", res.get('question'))
conv.append({"q":res['question'],"a":"Ya, benar"})
# Q2 service_status
r = requests.post(f"{BASE_URL}/generate-simulation-questions", json={"customer_id":"TA","topic":"winback","conversation":conv})
res = r.json()
print("Q2:", res.get('question'))
conv.append({"q":res['question'],"a":"Sudah berhenti"})
# Q3 reason_inquiry
r = requests.post(f"{BASE_URL}/generate-simulation-questions", json={"customer_id":"TA","topic":"winback","conversation":conv})
res = r.json()
print("Q3:", res.get('question'))
conv.append({"q":res['question'],"a":"Pindah rumah"})
# Q4 should be device_check
r = requests.post(f"{BASE_URL}/generate-simulation-questions", json={"customer_id":"TA","topic":"winback","conversation":conv})
res = r.json()
print("Q4:", res.get('question'))
print("is_closing:", res.get('is_closing'))
