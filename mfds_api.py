"""
식약처 건강기능식품 API 연동 스크립트
-------------------------------------
공공데이터포털 (data.go.kr) API를 사용하여
건강기능식품 제품 정보를 수집하고 JSON으로 저장합니다.

사용 전 준비:
1. https://www.data.go.kr 회원가입
2. "건강기능식품" 검색 후 아래 2개 API 활용 신청
   - 식품안전나라_건강기능식품 기능성 원료 현황
   - 식품안전나라_건강기능식품 품목 제조 보고
3. 발급받은 인증키를 API_KEY에 입력
"""

import requests
import json
import time
import csv
from datetime import datetime

# ============================================================
# ✅ 여기에 발급받은 인증키를 입력하세요
API_KEY = "cf50cb4181db460e9701"
# ============================================================

BASE_URL = "http://openapi.foodsafetykorea.go.kr/api"


# ============================================================
# 1. 건강기능식품 기능성 원료 목록 조회
# ============================================================
def get_functional_ingredients(start=1, end=100):
    """
    식약처 고시형/개별인정형 기능성 원료 목록을 가져옵니다.
    
    반환 데이터 예시:
    - 원료명: 비타민D
    - 기능성 내용: 골다공증 발생 위험 감소에 도움
    - 일일 섭취량: 50~100μg
    - 안전성 등급
    """
    url = f"{BASE_URL}/{API_KEY}/I0030/json/{start}/{end}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "I0030" not in data:
            print(f"❌ API 응답 오류: {data}")
            return []
        
        result = data["I0030"]
        
        if result.get("RESULT", {}).get("CODE") != "INFO-000":
            print(f"❌ API 오류: {result.get('RESULT', {}).get('MSG')}")
            return []
        
        rows = result.get("row", [])
        print(f"✅ 기능성 원료 {len(rows)}개 수집 완료")
        return rows
        
    except requests.exceptions.ConnectionError:
        print("❌ 네트워크 오류. 인터넷 연결을 확인하세요.")
        return []
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return []


# ============================================================
# 2. 건강기능식품 품목 제조보고 조회
# ============================================================
def get_products(product_name="", start=1, end=100):
    """
    시판 건강기능식품 제품 목록을 가져옵니다.
    
    반환 데이터 예시:
    - 제품명: 종근당 비타민D 2000IU
    - 업체명: 종근당건강
    - 기능성 원료명
    - 섭취방법
    - 유통기한
    """
    url = f"{BASE_URL}/{API_KEY}/I0030/json/{start}/{end}"
    params = {}
    if product_name:
        params["PRDT_NM"] = product_name
    
    # 건강기능식품 품목 제조보고 API 엔드포인트
    url = f"{BASE_URL}/{API_KEY}/C003/json/{start}/{end}"
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # API 코드별 처리
        for key in ["C003", "I0030", "RESULT"]:
            if key in data:
                result = data[key]
                rows = result.get("row", [])
                print(f"✅ 제품 {len(rows)}개 수집 완료")
                return rows
        
        print(f"❌ 예상치 못한 응답 구조: {list(data.keys())}")
        return []
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return []


# ============================================================
# 3. 수집 데이터를 앱용 형태로 가공
# ============================================================
def transform_ingredient(raw_ingredient):
    """
    식약처 원료 데이터를 앱 DB 형태로 변환합니다.
    """
    return {
        "name": raw_ingredient.get("RAWMTRL_NM", ""),           # 원료명
        "english_name": raw_ingredient.get("RAWMTRL_ENG_NM", ""), # 영문명
        "category": raw_ingredient.get("CLSFC_NO", ""),          # 분류번호
        "function": raw_ingredient.get("FNCLTY_CNTNT", ""),      # 기능성 내용
        "daily_intake": raw_ingredient.get("DAY_INTK_UPPR_QY", ""), # 일일 상한섭취량
        "safety_grade": classify_safety(raw_ingredient),          # 안전도 분류 (자체 로직)
        "kfda_approved": True,                                    # 식약처 인정 원료
        "source_type": raw_ingredient.get("RAWMTRL_TP", ""),     # 고시형/개별인정형
        "updated_at": datetime.now().isoformat(),
    }


def classify_safety(ingredient):
    """
    성분 데이터를 기반으로 안전도를 분류합니다.
    실제 서비스에서는 더 정교한 로직 필요.
    """
    name = ingredient.get("RAWMTRL_NM", "").lower()
    
    # 주의 성분 키워드
    caution_keywords = ["철", "아연", "요오드", "셀레늄", "구리", "망간"]
    warning_keywords = ["에페드린", "카페인"]
    
    if any(kw in name for kw in warning_keywords):
        return "warning"
    elif any(kw in name for kw in caution_keywords):
        return "caution"
    else:
        return "safe"


# ============================================================
# 4. 데이터 저장
# ============================================================
def save_to_json(data, filename):
    """JSON 파일로 저장 (Supabase 업로드용)"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 저장 완료: {filename} ({len(data)}개 항목)")


def save_to_csv(data, filename):
    """CSV 파일로 저장 (엑셀에서 확인용)"""
    if not data:
        print("❌ 저장할 데이터가 없습니다.")
        return
    
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"💾 CSV 저장 완료: {filename}")


# ============================================================
# 5. 메인 실행
# ============================================================
def main():
    print("=" * 50)
    print("🌿 필파인드 - 식약처 데이터 수집 시작")
    print("=" * 50)
    
    if API_KEY == "cf50cb4181db460e9701":
        print("\n⚠️  API_KEY를 먼저 설정하세요!")
        print("   1. https://www.data.go.kr 접속")
        print("   2. '건강기능식품 기능성 원료' 검색")
        print("   3. 활용 신청 후 인증키 발급")
        print("   4. 이 파일 상단 API_KEY = '발급받은키' 로 변경")
        print("\n💡 지금은 샘플 데이터로 테스트합니다...\n")
        
        # API 키 없이 테스트할 수 있는 샘플 데이터
        sample_ingredients = [
            {
                "name": "비타민D (콜레칼시페롤)",
                "english_name": "Vitamin D3 (Cholecalciferol)",
                "category": "비타민",
                "function": "칼슘과 인이 흡수되고 이용되는 데 필요. 뼈의 형성과 유지에 필요. 골다공증 발생 위험 감소에 도움.",
                "daily_intake": "100μg",
                "safety_grade": "safe",
                "kfda_approved": True,
                "source_type": "고시형",
                "updated_at": datetime.now().isoformat(),
            },
            {
                "name": "오메가-3 지방산",
                "english_name": "Omega-3 Fatty Acids (EPA+DHA)",
                "category": "지방산",
                "function": "혈중 중성지질 개선에 도움. 혈행 개선에 도움.",
                "daily_intake": "EPA+DHA 합계 2g",
                "safety_grade": "safe",
                "kfda_approved": True,
                "source_type": "고시형",
                "updated_at": datetime.now().isoformat(),
            },
            {
                "name": "마그네슘",
                "english_name": "Magnesium",
                "category": "미네랄",
                "function": "에너지 이용에 필요. 신경과 근육 기능 유지에 필요.",
                "daily_intake": "350mg",
                "safety_grade": "safe",
                "kfda_approved": True,
                "source_type": "고시형",
                "updated_at": datetime.now().isoformat(),
            },
            {
                "name": "루테인",
                "english_name": "Lutein",
                "category": "카로티노이드",
                "function": "노화로 인해 감소될 수 있는 황반색소 밀도를 유지하여 눈 건강에 도움.",
                "daily_intake": "20mg",
                "safety_grade": "safe",
                "kfda_approved": True,
                "source_type": "고시형",
                "updated_at": datetime.now().isoformat(),
            },
            {
                "name": "아연",
                "english_name": "Zinc",
                "category": "미네랄",
                "function": "정상적인 면역기능에 필요. 정상적인 세포분열에 필요.",
                "daily_intake": "35mg",
                "safety_grade": "caution",
                "kfda_approved": True,
                "source_type": "고시형",
                "updated_at": datetime.now().isoformat(),
            },
        ]
        
        save_to_json(sample_ingredients, "ingredients_sample.json")
        save_to_csv(sample_ingredients, "ingredients_sample.csv")
        
        print("\n✅ 샘플 데이터 생성 완료!")
        print("📁 생성된 파일:")
        print("   - ingredients_sample.json (Supabase 업로드용)")
        print("   - ingredients_sample.csv  (엑셀 확인용)")
        return
    
    # 실제 API 호출
    all_ingredients = []
    
    # 페이지네이션으로 전체 데이터 수집
    for page in range(1, 6):  # 최대 500개 수집
        start = (page - 1) * 100 + 1
        end = page * 100
        
        print(f"\n📥 페이지 {page}/5 수집 중... ({start}~{end}번)")
        raw_data = get_functional_ingredients(start, end)
        
        if not raw_data:
            print("   더 이상 데이터 없음. 수집 종료.")
            break
        
        # 데이터 변환
        transformed = [transform_ingredient(item) for item in raw_data]
        all_ingredients.extend(transformed)
        
        # API 요청 간격 (서버 부하 방지)
        time.sleep(0.5)
    
    if all_ingredients:
        save_to_json(all_ingredients, "ingredients_mfds.json")
        save_to_csv(all_ingredients, "ingredients_mfds.csv")
        
        print(f"\n🎉 수집 완료! 총 {len(all_ingredients)}개 원료 데이터")
        print("\n📋 다음 단계:")
        print("   1. ingredients_mfds.json → Supabase에 업로드")
        print("   2. 앱 코드에서 Supabase API로 데이터 불러오기")
    else:
        print("\n❌ 수집된 데이터가 없습니다. API 키를 확인하세요.")


if __name__ == "__main__":
    main()

