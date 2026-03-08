"""
Supabase DB 업로드 스크립트
-----------------------------
수집한 식약처 데이터를 Supabase에 저장합니다.

사용 전 준비:
1. https://supabase.com 에서 무료 프로젝트 생성
2. SQL 에디터에서 아래 테이블 생성 쿼리 실행
3. SUPABASE_URL, SUPABASE_KEY 입력
"""

import json
import requests

# ============================================================
# ✅ Supabase 설정 (프로젝트 Settings > API에서 확인)
SUPABASE_URL = "https://ymwchktzyovgffpdxvfy.supabase.co"
SUPABASE_KEY = "sb_publishable_XbGKYdXTFFgcDdrsO3ToHQ_C3BcCcic"
# ============================================================


def upload_ingredients(json_file="ingredients_sample.json"):
    """JSON 파일을 Supabase ingredients 테이블에 업로드"""
    
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    # 배치로 나눠서 업로드 (한번에 최대 500개)
    batch_size = 100
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/ingredients",
            headers=headers,
            json=batch
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ {i+1}~{i+len(batch)}번 업로드 완료")
        else:
            print(f"❌ 업로드 실패: {response.status_code} - {response.text}")
    
    print(f"\n🎉 총 {len(data)}개 원료 업로드 완료!")


if __name__ == "__main__":
    upload_ingredients()

