import json, urllib.request

SUPABASE_URL = "https://ymwchktzyovgffpdxvfy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltd2Noa3R6eW92Z2ZmcGR4dmZ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI4OTc5MzEsImV4cCI6MjA4ODQ3MzkzMX0.aooUSjOcif0bhxcW41Rb7e6AjkUkU4LL7UrjnbDvm-0"

with open("/tmp/mfds_data.json", encoding="utf-8") as f:
    data = json.load(f)

# 빈 name 제거 + 중복 방지
data = [d for d in data if d.get("name", "").strip()]
print(f"업로드 대상: {len(data)}개")

# 100개씩 나눠서 업로드
chunk_size = 100
success = 0
for i in range(0, len(data), chunk_size):
    chunk = data[i:i+chunk_size]
    body = json.dumps(chunk).encode("utf-8")
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/ingredients",
        data=body,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=ignore-duplicates"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as r:
            success += len(chunk)
            print(f"✅ {i+1}~{i+len(chunk)}: 업로드 완료")
    except Exception as e:
        print(f"❌ {i+1}~{i+len(chunk)}: {e}")

print(f"\n🎉 총 {success}개 Supabase 업로드 완료!")
