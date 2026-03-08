-- ============================================================
-- 필파인드 Supabase DB 스키마
-- Supabase > SQL Editor 에서 이 코드를 실행하세요
-- ============================================================

-- 1. 기능성 원료 테이블
CREATE TABLE ingredients (
  id           BIGSERIAL PRIMARY KEY,
  name         TEXT NOT NULL,            -- 원료명 (한글)
  english_name TEXT,                     -- 원료명 (영문)
  category     TEXT,                     -- 분류 (비타민/미네랄/지방산 등)
  function     TEXT,                     -- 기능성 내용
  daily_intake TEXT,                     -- 일일 상한섭취량
  safety_grade TEXT DEFAULT 'safe',      -- safe / caution / warning
  kfda_approved BOOLEAN DEFAULT true,   -- 식약처 인정 여부
  source_type  TEXT,                     -- 고시형 / 개별인정형
  updated_at   TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 제품 테이블
CREATE TABLE products (
  id              BIGSERIAL PRIMARY KEY,
  name            TEXT NOT NULL,         -- 제품명
  brand           TEXT,                  -- 브랜드명
  category        TEXT,                  -- 카테고리
  price           INTEGER,               -- 가격
  image_url       TEXT,                  -- 이미지 URL
  serving_size    TEXT,                  -- 1회 섭취량
  rating          DECIMAL(3,1),          -- 평점
  review_count    INTEGER DEFAULT 0,     -- 리뷰 수
  kfda_report_no  TEXT,                  -- 식약처 품목신고번호
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 제품-원료 연결 테이블 (다대다)
CREATE TABLE product_ingredients (
  id            BIGSERIAL PRIMARY KEY,
  product_id    BIGINT REFERENCES products(id) ON DELETE CASCADE,
  ingredient_id BIGINT REFERENCES ingredients(id) ON DELETE CASCADE,
  amount        TEXT,                    -- 함량 (예: 1000mg, 50μg)
  amount_unit   TEXT,                    -- 단위
  is_main       BOOLEAN DEFAULT false    -- 주요 기능성 원료 여부
);

-- 4. 검색 성능을 위한 인덱스
CREATE INDEX idx_ingredients_name ON ingredients USING gin(to_tsvector('simple', name));
CREATE INDEX idx_products_name ON products USING gin(to_tsvector('simple', name));
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_category ON products(category);

-- 5. 전문 검색 함수 (한글 성분/제품 검색)
CREATE OR REPLACE FUNCTION search_ingredients(query TEXT)
RETURNS SETOF ingredients AS $$
  SELECT * FROM ingredients
  WHERE name ILIKE '%' || query || '%'
     OR english_name ILIKE '%' || query || '%'
     OR category ILIKE '%' || query || '%'
     OR function ILIKE '%' || query || '%'
  ORDER BY 
    CASE WHEN name ILIKE query || '%' THEN 0 ELSE 1 END,
    name
  LIMIT 50;
$$ LANGUAGE sql STABLE;

