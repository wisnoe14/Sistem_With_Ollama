import requests

BASE_URL = "http://localhost:8000/api/v1/endpoints/conversation"

conv = []
print("== Test Winback Branch B (gangguan) ==")
# Step 1: greeting
r = requests.post(f"{BASE_URL}/generate-simulation-questions", json={"customer_id":"T1","topic":"winback","conversation":conv})
res = r.json()
print("Q1:", res.get('question'))
conv.append({"q":res['question'],"a":"Ya, benar"})
# Step 2: service_status
r = requests.post(f"{BASE_URL}/generate-simulation-questions", json={"customer_id":"T1","topic":"winback","conversation":conv})
res = r.json()
print("Q2:", res.get('question'))
conv.append({"q":res['question'],"a":"gangguan jaringan"})
# Step 3: expect complaint_apology (not closing)
r = requests.post(f"{BASE_URL}/generate-simulation-questions", json={"customer_id":"T1","topic":"winback","conversation":conv})
res = r.json()
print("Q3:", res.get('question'))
print("is_closing:", res.get('is_closing'))
