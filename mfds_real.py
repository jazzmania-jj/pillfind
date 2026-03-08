import urllib.request, json
from datetime import datetime

KEY = "cf50cb4181db460e9701"
BASE = f"http://openapi.foodsafetykorea.go.kr/api/{KEY}/I-0040/json"

all_data = []
page_size = 100

for start in range(1, 800, page_size):
    end = start + page_size - 1
    url = f"{BASE}/{start}/{end}"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read().decode('utf-8'))
            rows = data.get("I-0040", {}).get("row", [])
            if not rows:
                break
            all_data.extend(rows)
            print(f"✅ {start}~{end}: {len(rows)}개 수집 (총 {len(all_data)}개)")
    except Exception as e:
        print(f"❌ 에러: {e}")
        break

# Supabase용으로 변환
ingredients = []
for r in all_data:
    ingredients.append({
        "name": r.get("APLC_RAWMTRL_NM", ""),
        "english_name": "",
        "category": r.get("INDUTY_NM", ""),
        "function": r.get("FNCLTY_CN", ""),
        "daily_intake": r.get("DAY_INTK_CN", ""),
        "safety_grade": "caution" if r.get("IFTKN_ATNT_MATR_CN") else "safe",
        "kfda_approved": True,
        "source_type": "개별인정형",
        "updated_at": datetime.now().isoformat()
    })

with open("/tmp/mfds_data.json", "w", encoding="utf-8") as f:
    json.dump(ingredients, f, ensure_ascii=False, indent=2)

print(f"\n🎉 완료! 총 {len(ingredients)}개 저장 → /tmp/mfds_data.json")
