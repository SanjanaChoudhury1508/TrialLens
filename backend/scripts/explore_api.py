import json
import requests

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

params = {
    "query.term": "lung cancer",
    "pageSize": 5,
}

response = requests.get(BASE_URL, params=params)
response.raise_for_status()

data = response.json()

with open("sample_response.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Response saved to sample_response.json")