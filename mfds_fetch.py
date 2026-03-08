import urllib.request
import json

API_KEY = "cf50cb4181db460e9701"
BASE_URL = "http://openapi.foodsafetykorea.go.kr/api"

url = f"{BASE_URL}/{API_KEY}/I0030/json/1/100"
print(f"요청 URL: {url}")

try:
    with urllib.request.urlopen(url) as res:
        data = json.loads(res.read().decode())
        print("성공!")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
except Exception as e:
    print(f"에러: {e}")
