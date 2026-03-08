import urllib.request
import json

SUPABASE_URL = "https://ymwchktzyovgffpdxvfy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltd2Noa3R6eW92Z2ZmcGR4dmZ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI4OTc5MzEsImV4cCI6MjA4ODQ3MzkzMX0.aooUSjOcif0bhxcW41Rb7e6AjkUkU4LL7UrjnbDvm-0"

ingredients = [
    {"name": "비타민C (아스코르브산)", "english_name": "Vitamin C (Ascorbic Acid)", "category": "비타민", "function": "항산화 작용, 콜라겐 합성, 면역력 강화에 도움", "daily_intake": "100mg", "safety_grade": "safe"},
    {"name": "비타민B1 (티아민)", "english_name": "Vitamin B1 (Thiamine)", "category": "비타민", "function": "탄수화물 대사, 신경 기능 유지에 필요", "daily_intake": "1.2mg", "safety_grade": "safe"},
    {"name": "비타민B2 (리보플라빈)", "english_name": "Vitamin B2 (Riboflavin)", "category": "비타민", "function": "에너지 대사, 세포 성장 및 발달에 필요", "daily_intake": "1.4mg", "safety_grade": "safe"},
    {"name": "비타민B3 (나이아신)", "english_name": "Vitamin B3 (Niacin)", "category": "비타민", "function": "에너지 대사, 피부 건강 유지에 도움", "daily_intake": "15mg", "safety_grade": "caution"},
    {"name": "비타민B5 (판토텐산)", "english_name": "Vitamin B5 (Pantothenic Acid)", "category": "비타민", "function": "에너지 대사, 스트레스 호르몬 합성에 필요", "daily_intake": "5mg", "safety_grade": "safe"},
    {"name": "비타민B6 (피리독신)", "english_name": "Vitamin B6 (Pyridoxine)", "category": "비타민", "function": "단백질 대사, 신경전달물질 합성에 필요", "daily_intake": "1.5mg", "safety_grade": "safe"},
    {"name": "비타민B7 (비오틴)", "english_name": "Vitamin B7 (Biotin)", "category": "비타민", "function": "지방 및 탄수화물 대사, 모발·손톱 건강에 도움", "daily_intake": "30mcg", "safety_grade": "safe"},
    {"name": "비타민B9 (엽산)", "english_name": "Vitamin B9 (Folic Acid)", "category": "비타민", "function": "세포 분열, 임산부 태아 신경관 발달에 필요", "daily_intake": "400mcg", "safety_grade": "safe"},
    {"name": "비타민B12 (코발라민)", "english_name": "Vitamin B12 (Cobalamin)", "category": "비타민", "function": "적혈구 생성, 신경 기능 유지에 필요", "daily_intake": "2.4mcg", "safety_grade": "safe"},
    {"name": "비타민E (토코페롤)", "english_name": "Vitamin E (Tocopherol)", "category": "비타민", "function": "항산화 작용, 세포막 보호, 면역력 강화에 도움", "daily_intake": "15mg", "safety_grade": "safe"},
    {"name": "비타민K", "english_name": "Vitamin K", "category": "비타민", "function": "혈액 응고, 뼈 건강 유지에 필요", "daily_intake": "120mcg", "safety_grade": "caution"},
    {"name": "비타민A (레티놀)", "english_name": "Vitamin A (Retinol)", "category": "비타민", "function": "시력 유지, 면역 기능, 피부 건강에 필요", "daily_intake": "700mcg", "safety_grade": "caution"},
    {"name": "칼슘", "english_name": "Calcium", "category": "미네랄", "function": "뼈와 치아 형성, 근육 수축, 신경 전달에 필요", "daily_intake": "700mg", "safety_grade": "safe"},
    {"name": "철분", "english_name": "Iron", "category": "미네랄", "function": "적혈구 헤모글로빈 구성, 산소 운반에 필요", "daily_intake": "14mg", "safety_grade": "caution"},
    {"name": "칼륨", "english_name": "Potassium", "category": "미네랄", "function": "심장 기능, 혈압 조절, 근육 기능 유지에 필요", "daily_intake": "3500mg", "safety_grade": "safe"},
    {"name": "셀레늄", "english_name": "Selenium", "category": "미네랄", "function": "항산화 효소 구성, 갑상선 기능 유지에 필요", "daily_intake": "60mcg", "safety_grade": "caution"},
    {"name": "구리", "english_name": "Copper", "category": "미네랄", "function": "철분 흡수, 결합조직 형성, 항산화에 필요", "daily_intake": "0.8mg", "safety_grade": "safe"},
    {"name": "망간", "english_name": "Manganese", "category": "미네랄", "function": "뼈 형성, 에너지 대사, 항산화에 필요", "daily_intake": "3mg", "safety_grade": "safe"},
    {"name": "요오드", "english_name": "Iodine", "category": "미네랄", "function": "갑상선 호르몬 합성, 신진대사 조절에 필요", "daily_intake": "150mcg", "safety_grade": "caution"},
    {"name": "크롬", "english_name": "Chromium", "category": "미네랄", "function": "혈당 조절, 인슐린 작용 보조에 도움", "daily_intake": "35mcg", "safety_grade": "safe"},
    {"name": "몰리브덴", "english_name": "Molybdenum", "category": "미네랄", "function": "효소 구성, 아미노산 대사에 필요", "daily_intake": "45mcg", "safety_grade": "safe"},
    {"name": "오메가3 지방산 (EPA)", "english_name": "Omega-3 (EPA)", "category": "지방산", "function": "혈중 중성지방 감소, 항염증 작용에 도움", "daily_intake": "EPA+DHA 합계 500mg", "safety_grade": "safe"},
    {"name": "오메가3 지방산 (DHA)", "english_name": "Omega-3 (DHA)", "category": "지방산", "function": "뇌 기능 유지, 시력 보호, 항염증 작용에 도움", "daily_intake": "EPA+DHA 합계 500mg", "safety_grade": "safe"},
    {"name": "감마리놀렌산 (GLA)", "english_name": "Gamma-Linolenic Acid (GLA)", "category": "지방산", "function": "피부 장벽 기능 유지, 항염증 작용에 도움", "daily_intake": "240mg", "safety_grade": "safe"},
    {"name": "공액리놀레산 (CLA)", "english_name": "Conjugated Linoleic Acid (CLA)", "category": "지방산", "function": "체지방 감소, 근육량 유지에 도움", "daily_intake": "3g", "safety_grade": "safe"},
    {"name": "L-카르니틴", "english_name": "L-Carnitine", "category": "아미노산", "function": "지방산 운반, 에너지 생성, 운동 능력 향상에 도움", "daily_intake": "500mg", "safety_grade": "safe"},
    {"name": "L-아르기닌", "english_name": "L-Arginine", "category": "아미노산", "function": "혈관 확장, 혈류 개선, 면역 기능에 도움", "daily_intake": "3g", "safety_grade": "caution"},
    {"name": "L-글루타민", "english_name": "L-Glutamine", "category": "아미노산", "function": "장 건강, 면역 기능, 근육 회복에 도움", "daily_intake": "5g", "safety_grade": "safe"},
    {"name": "L-시스테인", "english_name": "L-Cysteine", "category": "아미노산", "function": "항산화 글루타치온 합성, 모발·피부 건강에 도움", "daily_intake": "500mg", "safety_grade": "safe"},
    {"name": "BCAA (분지사슬아미노산)", "english_name": "BCAA (Branched-Chain Amino Acids)", "category": "아미노산", "function": "근육 합성 촉진, 운동 후 근육 회복에 도움", "daily_intake": "5g", "safety_grade": "safe"},
    {"name": "타우린", "english_name": "Taurine", "category": "아미노산", "function": "심장 기능, 눈 건강, 항산화 작용에 도움", "daily_intake": "500mg", "safety_grade": "safe"},
    {"name": "글리신", "english_name": "Glycine", "category": "아미노산", "function": "콜라겐 합성, 수면 개선, 항산화에 도움", "daily_intake": "3g", "safety_grade": "safe"},
    {"name": "강황 (커큐민)", "english_name": "Turmeric (Curcumin)", "category": "식물추출물", "function": "항염증, 항산화, 관절 건강에 도움", "daily_intake": "500mg", "safety_grade": "safe"},
    {"name": "홍삼", "english_name": "Red Ginseng", "category": "식물추출물", "function": "면역력 증진, 피로 회복, 기억력 개선에 도움", "daily_intake": "3g", "safety_grade": "safe"},
    {"name": "은행잎 추출물", "english_name": "Ginkgo Biloba Extract", "category": "식물추출물", "function": "혈액순환 개선, 기억력 향상, 항산화에 도움", "daily_intake": "120mg", "safety_grade": "caution"},
    {"name": "밀크씨슬 (실리마린)", "english_name": "Milk Thistle (Silymarin)", "category": "식물추출물", "function": "간 세포 보호, 간 기능 개선에 도움", "daily_intake": "200mg", "safety_grade": "safe"},
    {"name": "포도씨 추출물", "english_name": "Grape Seed Extract", "category": "식물추출물", "function": "항산화, 혈관 건강, 피부 탄력에 도움", "daily_intake": "100mg", "safety_grade": "safe"},
    {"name": "녹차 추출물 (EGCG)", "english_name": "Green Tea Extract (EGCG)", "category": "식물추출물", "function": "항산화, 체지방 감소, 항염증에 도움", "daily_intake": "400mg", "safety_grade": "caution"},
    {"name": "아슈와간다", "english_name": "Ashwagandha", "category": "식물추출물", "function": "스트레스 감소, 피로 회복, 수면 개선에 도움", "daily_intake": "600mg", "safety_grade": "safe"},
    {"name": "마카 추출물", "english_name": "Maca Extract", "category": "식물추출물", "function": "활력 증진, 호르몬 균형, 생식 건강에 도움", "daily_intake": "1500mg", "safety_grade": "safe"},
    {"name": "쏘팔메토", "english_name": "Saw Palmetto", "category": "식물추출물", "function": "전립선 건강, 남성 호르몬 균형 유지에 도움", "daily_intake": "320mg", "safety_grade": "safe"},
    {"name": "바코파 모니에리", "english_name": "Bacopa Monnieri", "category": "식물추출물", "function": "기억력 개선, 인지 기능 향상, 스트레스 감소에 도움", "daily_intake": "300mg", "safety_grade": "safe"},
    {"name": "엘더베리", "english_name": "Elderberry", "category": "식물추출물", "function": "면역력 강화, 항바이러스, 항산화에 도움", "daily_intake": "600mg", "safety_grade": "safe"},
    {"name": "락토바실러스 아시도필러스", "english_name": "Lactobacillus Acidophilus", "category": "프로바이오틱스", "function": "장 건강, 유해균 억제, 소화 개선에 도움", "daily_intake": "10억 CFU", "safety_grade": "safe"},
    {"name": "비피도박테리움 롱검", "english_name": "Bifidobacterium Longum", "category": "프로바이오틱스", "function": "장 운동 촉진, 면역 기능, 변비 개선에 도움", "daily_intake": "10억 CFU", "safety_grade": "safe"},
    {"name": "이눌린 (프리바이오틱스)", "english_name": "Inulin (Prebiotic)", "category": "프리바이오틱스", "function": "유익균 성장 촉진, 장 건강, 혈당 안정에 도움", "daily_intake": "5g", "safety_grade": "safe"},
    {"name": "프락토올리고당 (FOS)", "english_name": "Fructooligosaccharides (FOS)", "category": "프리바이오틱스", "function": "장내 유익균 증식, 소화 건강에 도움", "daily_intake": "3g", "safety_grade": "safe"},
    {"name": "코엔자임Q10", "english_name": "Coenzyme Q10 (CoQ10)", "category": "항산화", "function": "세포 에너지 생성, 항산화, 심장 건강에 도움", "daily_intake": "100mg", "safety_grade": "safe"},
    {"name": "알파리포산", "english_name": "Alpha-Lipoic Acid (ALA)", "category": "항산화", "function": "강력한 항산화, 혈당 조절, 신경 보호에 도움", "daily_intake": "300mg", "safety_grade": "safe"},
    {"name": "레스베라트롤", "english_name": "Resveratrol", "category": "항산화", "function": "항산화, 항염증, 심혈관 건강에 도움", "daily_intake": "150mg", "safety_grade": "safe"},
    {"name": "아스타잔틴", "english_name": "Astaxanthin", "category": "항산화", "function": "강력한 항산화, 피부 건강, 눈 건강에 도움", "daily_intake": "6mg", "safety_grade": "safe"},
    {"name": "퀘르세틴", "english_name": "Quercetin", "category": "항산화", "function": "항염증, 항산화, 알레르기 완화에 도움", "daily_intake": "500mg", "safety_grade": "safe"},
    {"name": "글루코사민", "english_name": "Glucosamine", "category": "관절건강", "function": "연골 구성 성분, 관절 통증 완화, 관절 건강 유지에 도움", "daily_intake": "1500mg", "safety_grade": "safe"},
    {"name": "콘드로이틴", "english_name": "Chondroitin", "category": "관절건강", "function": "연골 탄력 유지, 관절 수분 보호에 도움", "daily_intake": "1200mg", "safety_grade": "safe"},
    {"name": "히알루론산", "english_name": "Hyaluronic Acid", "category": "관절건강", "function": "관절 윤활, 피부 수분 유지에 도움", "daily_intake": "120mg", "safety_grade": "safe"},
    {"name": "MSM (메틸설포닐메탄)", "english_name": "MSM (Methylsulfonylmethane)", "category": "관절건강", "function": "관절 염증 감소, 통증 완화, 연골 보호에 도움", "daily_intake": "1500mg", "safety_grade": "safe"},
    {"name": "콜라겐 펩타이드", "english_name": "Collagen Peptide", "category": "관절건강", "function": "피부 탄력, 관절 건강, 뼈 강도 유지에 도움", "daily_intake": "5g", "safety_grade": "safe"},
    {"name": "빌베리 추출물", "english_name": "Bilberry Extract", "category": "눈건강", "function": "눈의 피로 회복, 야간 시력 개선에 도움", "daily_intake": "160mg", "safety_grade": "safe"},
    {"name": "제아잔틴", "english_name": "Zeaxanthin", "category": "눈건강", "function": "황반 색소 밀도 유지, 눈 건강 보호에 도움", "daily_intake": "2mg", "safety_grade": "safe"},
    {"name": "멜라토닌", "english_name": "Melatonin", "category": "수면", "function": "수면 리듬 조절, 시차 적응, 수면의 질 개선에 도움", "daily_intake": "0.5mg", "safety_grade": "caution"},
    {"name": "마그네슘 글리시네이트", "english_name": "Magnesium Glycinate", "category": "수면", "function": "신경 안정, 수면 개선, 근육 이완에 도움", "daily_intake": "200mg", "safety_grade": "safe"},
    {"name": "L-테아닌", "english_name": "L-Theanine", "category": "수면", "function": "스트레스 완화, 집중력 향상, 수면 질 개선에 도움", "daily_intake": "200mg", "safety_grade": "safe"},
    {"name": "발레리안 뿌리", "english_name": "Valerian Root", "category": "수면", "function": "수면 개선, 불안 감소, 신경 안정에 도움", "daily_intake": "600mg", "safety_grade": "safe"},
    {"name": "가르시니아 캄보지아", "english_name": "Garcinia Cambogia", "category": "다이어트", "function": "식욕 억제, 지방 합성 억제에 도움", "daily_intake": "1500mg", "safety_grade": "caution"},
    {"name": "키토산", "english_name": "Chitosan", "category": "다이어트", "function": "지방 흡수 억제, 체중 관리에 도움", "daily_intake": "3g", "safety_grade": "safe"},
    {"name": "녹차 카테킨", "english_name": "Green Tea Catechin", "category": "다이어트", "function": "체지방 감소, 에너지 대사 촉진에 도움", "daily_intake": "300mg", "safety_grade": "safe"},
    {"name": "세라마이드", "english_name": "Ceramide", "category": "피부건강", "function": "피부 장벽 강화, 보습, 피부 건강 유지에 도움", "daily_intake": "30mg", "safety_grade": "safe"},
    {"name": "피크노제놀", "english_name": "Pycnogenol", "category": "피부건강", "function": "강력한 항산화, 피부 탄력, 혈관 건강에 도움", "daily_intake": "100mg", "safety_grade": "safe"},
]

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

success = 0
fail = 0

for item in ingredients:
    data = json.dumps(item).encode("utf-8")
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/ingredients",
        data=data,
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as res:
            success += 1
            print(f"✅ {item['name']}")
    except Exception as e:
        fail += 1
        print(f"❌ {item['name']}: {e}")

print(f"\n완료! 성공: {success}개, 실패: {fail}개")
