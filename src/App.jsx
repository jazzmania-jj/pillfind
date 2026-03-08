import { useState, useEffect } from "react";

// ============================================================
// ✅ 여기에 Supabase 정보를 입력하세요
// Settings > API Keys 에서 확인
const SUPABASE_URL = "https://ymwchktzyovgffpdxvfy.supabase.co";
const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltd2Noa3R6eW92Z2ZmcGR4dmZ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI4OTc5MzEsImV4cCI6MjA4ODQ3MzkzMX0.aooUSjOcif0bhxcW41Rb7e6AjkUkU4LL7UrjnbDvm-0";
// ============================================================

// Supabase에서 데이터 가져오는 함수
async function fetchIngredients(searchQuery = "") {
  let url = `${SUPABASE_URL}/rest/v1/ingredients?select=*&order=name`;

  // 검색어가 있으면 필터 추가
  if (searchQuery) {
    url += `&or=(name.ilike.*${searchQuery}*,category.ilike.*${searchQuery}*)`;
  }

  const response = await fetch(url, {
    headers: {
      apikey: SUPABASE_KEY,
      Authorization: `Bearer ${SUPABASE_KEY}`,
    },
  });

  if (!response.ok) throw new Error("데이터를 불러오지 못했습니다");
  return await response.json();
}

async function analyzeWithAI(ingredient, question) {
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1000,
      system: `당신은 '김약사'입니다. 약학 전문 지식을 바탕으로 소비자들이 영양제 성분을 이해할 수 있도록 돕는 약사입니다.
- 전문적이지만 쉽고 친근하게 설명
- 과장하지 않고 근거 기반으로 말함
- MFDS(식약처) 기준 항상 참고
- 200자 이내로 핵심만 간결하게
- 반드시 한국어로 답변`,
      messages: [
        {
          role: "user",
          content: `성분: ${ingredient.name}
기능성: ${ingredient.function || ""}
일일 상한섭취량: ${ingredient.daily_intake || ""}
질문: ${question}`,
        },
      ],
    }),
  });
  const data = await response.json();
  return data.content[0].text;
}

const SAFETY_CONFIG = {
  safe: { label: "안전", color: "#22c55e", bg: "#f0fdf4", icon: "✓" },
  caution: { label: "주의", color: "#f59e0b", bg: "#fffbeb", icon: "!" },
  warning: { label: "경고", color: "#ef4444", bg: "#fef2f2", icon: "✕" },
};

export default function SupplementAnalyzer() {
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selected, setSelected] = useState(null);
  const [aiComment, setAiComment] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [customQuestion, setCustomQuestion] = useState("");
  const [compareList, setCompareList] = useState([]);
  const [activeTab, setActiveTab] = useState("search");

  // 컴포넌트 시작 시 Supabase에서 데이터 불러오기
  useEffect(() => {
    loadIngredients();
  }, []);

  // 검색어 변경 시 자동 검색
  useEffect(() => {
    const timer = setTimeout(() => {
      loadIngredients(searchQuery);
    }, 300); // 0.3초 딜레이 (타이핑 중 과도한 요청 방지)
    return () => clearTimeout(timer);
  }, [searchQuery]);

  async function loadIngredients(query = "") {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchIngredients(query);
      setIngredients(data);
    } catch (e) {
      setError("데이터를 불러오지 못했습니다. Supabase 연결을 확인해주세요.");
    }
    setLoading(false);
  }

  async function handleSelectIngredient(ingredient) {
    setSelected(ingredient);
    setActiveTab("detail");
    setAiComment("");
    setAiLoading(true);
    try {
      const comment = await analyzeWithAI(ingredient, "이 성분의 핵심 효능과 복용 시 주의사항을 알려주세요.");
      setAiComment(comment);
    } catch {
      setAiComment("AI 분석 오류가 발생했습니다.");
    }
    setAiLoading(false);
  }

  async function handleAskQuestion() {
    if (!customQuestion.trim() || !selected) return;
    setAiLoading(true);
    try {
      const comment = await analyzeWithAI(selected, customQuestion);
      setAiComment(comment);
      setCustomQuestion("");
    } catch {
      setAiComment("오류가 발생했습니다. 다시 시도해주세요.");
    }
    setAiLoading(false);
  }

  const toggleCompare = (item) => {
    setCompareList((prev) => {
      if (prev.find((p) => p.id === item.id)) return prev.filter((p) => p.id !== item.id);
      if (prev.length >= 2) return [prev[1], item];
      return [...prev, item];
    });
  };

  return (
    <div style={{ fontFamily: "'Noto Sans KR', sans-serif", minHeight: "100vh", background: "#f8fafc" }}>
      {/* Header */}
      <header style={{ background: "#fff", borderBottom: "1px solid #e2e8f0", position: "sticky", top: 0, zIndex: 100, boxShadow: "0 1px 3px rgba(0,0,0,0.06)" }}>
        <div style={{ maxWidth: 900, margin: "0 auto", padding: "0 20px", height: 60, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 36, height: 36, background: "linear-gradient(135deg, #10b981, #059669)", borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>💊</div>
            <div>
              <div style={{ fontSize: 17, fontWeight: 800, color: "#0f172a" }}>영리하다</div>
              <div style={{ fontSize: 10, color: "#64748b" }}>영양제 리뷰를 하다, 영리하다</div>
            </div>
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            {[
              { key: "search", label: "성분 검색" },
              { key: "compare", label: `비교${compareList.length > 0 ? ` (${compareList.length})` : ""}` },
            ].map((tab) => (
              <button key={tab.key} onClick={() => setActiveTab(tab.key)}
                style={{ padding: "6px 14px", borderRadius: 8, border: "none", cursor: "pointer", fontSize: 13, fontWeight: 600, background: activeTab === tab.key ? "#10b981" : "transparent", color: activeTab === tab.key ? "#fff" : "#64748b" }}>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main style={{ maxWidth: 900, margin: "0 auto", padding: "24px 20px" }}>

        {/* 검색 탭 */}
        {(activeTab === "search" || activeTab === "detail") && (
          <>
            {/* 검색창 */}
            <div style={{ marginBottom: 24 }}>
              <div style={{ position: "relative" }}>
                <span style={{ position: "absolute", left: 16, top: "50%", transform: "translateY(-50%)", fontSize: 18, color: "#94a3b8" }}>🔍</span>
                <input
                  value={searchQuery}
                  onChange={(e) => { setSearchQuery(e.target.value); setActiveTab("search"); }}
                  placeholder="성분명, 카테고리로 검색 (예: 비타민D, 미네랄, 오메가3)"
                  style={{ width: "100%", padding: "14px 16px 14px 48px", borderRadius: 14, border: "2px solid #e2e8f0", fontSize: 15, outline: "none", background: "#fff", boxSizing: "border-box" }}
                  onFocus={(e) => (e.target.style.borderColor = "#10b981")}
                  onBlur={(e) => (e.target.style.borderColor = "#e2e8f0")}
                />
              </div>
              {/* 빠른 검색 태그 */}
              <div style={{ display: "flex", gap: 8, marginTop: 12, flexWrap: "wrap" }}>
                {["비타민", "미네랄", "오메가", "마그네슘", "루테인", "프로바이오틱스"].map((tag) => (
                  <button key={tag} onClick={() => { setSearchQuery(tag); setActiveTab("search"); }}
                    style={{ padding: "5px 12px", borderRadius: 20, border: "1px solid #d1fae5", background: "#ecfdf5", color: "#059669", fontSize: 12, fontWeight: 600, cursor: "pointer" }}>
                    #{tag}
                  </button>
                ))}
              </div>
            </div>

            {/* 성분 상세 */}
            {activeTab === "detail" && selected ? (
              <div>
                <button onClick={() => setActiveTab("search")}
                  style={{ display: "flex", alignItems: "center", gap: 6, color: "#10b981", background: "none", border: "none", cursor: "pointer", fontSize: 14, fontWeight: 600, marginBottom: 16 }}>
                  ← 검색결과로 돌아가기
                </button>

                {/* 성분 기본 정보 */}
                <div style={{ background: "#fff", borderRadius: 16, padding: 24, boxShadow: "0 1px 3px rgba(0,0,0,0.08)", marginBottom: 16 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div>
                      <div style={{ fontSize: 11, color: "#10b981", fontWeight: 700, marginBottom: 4 }}>{selected.category}</div>
                      <div style={{ fontSize: 22, fontWeight: 800, color: "#0f172a", marginBottom: 4 }}>{selected.name}</div>
                      {selected.english_name && (
                        <div style={{ fontSize: 13, color: "#94a3b8" }}>{selected.english_name}</div>
                      )}
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 6, alignItems: "flex-end" }}>
                      {selected.kfda_approved && (
                        <span style={{ background: "#dbeafe", color: "#2563eb", fontSize: 12, fontWeight: 700, padding: "4px 10px", borderRadius: 20 }}>✓ 식약처 인정</span>
                      )}
                      <span style={{
                        background: SAFETY_CONFIG[selected.safety_grade]?.bg || "#f0fdf4",
                        color: SAFETY_CONFIG[selected.safety_grade]?.color || "#22c55e",
                        fontSize: 12, fontWeight: 700, padding: "4px 10px", borderRadius: 20
                      }}>
                        {SAFETY_CONFIG[selected.safety_grade]?.label || "안전"}
                      </span>
                    </div>
                  </div>

                  {selected.function && (
                    <div style={{ marginTop: 16, padding: 16, background: "#f8fafc", borderRadius: 12 }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: "#475569", marginBottom: 6 }}>📋 기능성 내용 (식약처 인정)</div>
                      <div style={{ fontSize: 14, color: "#374151", lineHeight: 1.7 }}>{selected.function}</div>
                    </div>
                  )}

                  {selected.daily_intake && (
                    <div style={{ marginTop: 10, padding: 16, background: "#fffbeb", borderRadius: 12, border: "1px solid #fde68a" }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: "#92400e", marginBottom: 4 }}>⚠️ 일일 상한 섭취량</div>
                      <div style={{ fontSize: 14, color: "#78350f", fontWeight: 600 }}>{selected.daily_intake}</div>
                    </div>
                  )}
                </div>

                {/* 김약사 AI 코멘트 */}
                <div style={{ background: "linear-gradient(135deg, #ecfdf5, #f0fdf4)", borderRadius: 16, padding: 24, border: "1px solid #a7f3d0", marginBottom: 16 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
                    <div style={{ width: 40, height: 40, background: "linear-gradient(135deg, #10b981, #059669)", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>💬</div>
                    <div>
                      <div style={{ fontSize: 15, fontWeight: 800, color: "#064e3b" }}>김약사 한마디</div>
                      <div style={{ fontSize: 11, color: "#059669" }}>AI 기반 전문 분석</div>
                    </div>
                  </div>
                  {aiLoading ? (
                    <div style={{ display: "flex", alignItems: "center", gap: 8, color: "#059669" }}>
                      <div style={{ width: 16, height: 16, border: "2px solid #10b981", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 1s linear infinite" }} />
                      <span style={{ fontSize: 14 }}>분석 중...</span>
                    </div>
                  ) : (
                    <p style={{ fontSize: 14, color: "#065f46", lineHeight: 1.7, margin: 0 }}>{aiComment}</p>
                  )}
                  <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
                    <input
                      value={customQuestion}
                      onChange={(e) => setCustomQuestion(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleAskQuestion()}
                      placeholder="김약사에게 직접 물어보세요 (예: 임산부가 먹어도 되나요?)"
                      style={{ flex: 1, padding: "10px 14px", borderRadius: 10, border: "1px solid #a7f3d0", fontSize: 13, outline: "none", background: "#fff" }}
                    />
                    <button onClick={handleAskQuestion} disabled={aiLoading}
                      style={{ padding: "10px 18px", borderRadius: 10, border: "none", background: "#10b981", color: "#fff", fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
                      질문
                    </button>
                  </div>
                </div>

                <button onClick={() => toggleCompare(selected)}
                  style={{ width: "100%", padding: 14, borderRadius: 12, border: `2px solid ${compareList.find(p => p.id === selected.id) ? "#ef4444" : "#10b981"}`, background: compareList.find(p => p.id === selected.id) ? "#fef2f2" : "#ecfdf5", color: compareList.find(p => p.id === selected.id) ? "#ef4444" : "#059669", fontSize: 14, fontWeight: 700, cursor: "pointer" }}>
                  {compareList.find(p => p.id === selected.id) ? "비교에서 제거" : "+ 비교에 추가"}
                </button>
              </div>

            ) : (
              /* 성분 목록 */
              <div>
                {/* DB 연결 상태 표시 */}
                {!loading && !error && (
                  <div style={{ fontSize: 13, color: "#94a3b8", marginBottom: 12 }}>
                    🟢 Supabase 연결됨 · 총 <strong>{ingredients.length}개</strong> 성분
                  </div>
                )}

                {/* 로딩 */}
                {loading && (
                  <div style={{ textAlign: "center", padding: 48, color: "#94a3b8" }}>
                    <div style={{ fontSize: 32, marginBottom: 12 }}>⏳</div>
                    <div style={{ fontSize: 15, fontWeight: 600 }}>Supabase에서 데이터 불러오는 중...</div>
                  </div>
                )}

                {/* 에러 */}
                {error && (
                  <div style={{ textAlign: "center", padding: 48, background: "#fef2f2", borderRadius: 16 }}>
                    <div style={{ fontSize: 32, marginBottom: 12 }}>❌</div>
                    <div style={{ fontSize: 15, fontWeight: 600, color: "#ef4444" }}>{error}</div>
                    <div style={{ fontSize: 13, color: "#94a3b8", marginTop: 8 }}>SUPABASE_URL과 SUPABASE_KEY를 확인해주세요</div>
                    <button onClick={() => loadIngredients(searchQuery)}
                      style={{ marginTop: 16, padding: "10px 24px", borderRadius: 10, border: "none", background: "#10b981", color: "#fff", fontSize: 14, fontWeight: 700, cursor: "pointer" }}>
                      다시 시도
                    </button>
                  </div>
                )}

                {/* 결과 없음 */}
                {!loading && !error && ingredients.length === 0 && (
                  <div style={{ textAlign: "center", padding: 48, color: "#94a3b8" }}>
                    <div style={{ fontSize: 40, marginBottom: 12 }}>🔍</div>
                    <div style={{ fontSize: 16, fontWeight: 600 }}>검색 결과가 없습니다</div>
                    <div style={{ fontSize: 14, marginTop: 4 }}>다른 키워드로 검색해보세요</div>
                  </div>
                )}

                {/* 성분 카드 목록 */}
                {!loading && !error && (
                  <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                    {ingredients.map((ingredient) => {
                      const cfg = SAFETY_CONFIG[ingredient.safety_grade] || SAFETY_CONFIG.safe;
                      return (
                        <div key={ingredient.id}
                          onClick={() => handleSelectIngredient(ingredient)}
                          style={{ background: "#fff", borderRadius: 14, padding: 20, display: "flex", alignItems: "center", gap: 16, cursor: "pointer", border: "2px solid transparent", boxShadow: "0 1px 3px rgba(0,0,0,0.06)", transition: "all 0.2s" }}
                          onMouseEnter={(e) => { e.currentTarget.style.borderColor = "#10b981"; e.currentTarget.style.boxShadow = "0 4px 12px rgba(16,185,129,0.15)"; }}
                          onMouseLeave={(e) => { e.currentTarget.style.borderColor = "transparent"; e.currentTarget.style.boxShadow = "0 1px 3px rgba(0,0,0,0.06)"; }}>
                          <div style={{ width: 48, height: 48, borderRadius: 12, background: cfg.bg, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22, flexShrink: 0 }}>
                            {ingredient.category?.includes("비타민") ? "🌟" : ingredient.category?.includes("미네랄") ? "🔵" : ingredient.category?.includes("지방") ? "🐟" : "💊"}
                          </div>
                          <div style={{ flex: 1 }}>
                            <div style={{ fontSize: 11, color: "#10b981", fontWeight: 700 }}>{ingredient.category}</div>
                            <div style={{ fontSize: 16, fontWeight: 800, color: "#0f172a", marginBottom: 2 }}>{ingredient.name}</div>
                            {ingredient.english_name && (
                              <div style={{ fontSize: 12, color: "#94a3b8" }}>{ingredient.english_name}</div>
                            )}
                            {ingredient.function && (
                              <div style={{ fontSize: 12, color: "#64748b", marginTop: 4, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 400 }}>{ingredient.function}</div>
                            )}
                          </div>
                          <div style={{ textAlign: "right", flexShrink: 0 }}>
                            {ingredient.kfda_approved && (
                              <div style={{ fontSize: 10, color: "#2563eb", fontWeight: 700, marginBottom: 4 }}>✓ 식약처</div>
                            )}
                            <span style={{ background: cfg.bg, color: cfg.color, fontSize: 12, fontWeight: 700, padding: "3px 10px", borderRadius: 20 }}>{cfg.label}</span>
                            <button onClick={(e) => { e.stopPropagation(); toggleCompare(ingredient); }}
                              style={{ display: "block", marginTop: 6, padding: "3px 10px", borderRadius: 8, border: `1px solid ${compareList.find(p => p.id === ingredient.id) ? "#ef4444" : "#d1d5db"}`, background: compareList.find(p => p.id === ingredient.id) ? "#fef2f2" : "#f9fafb", color: compareList.find(p => p.id === ingredient.id) ? "#ef4444" : "#6b7280", fontSize: 11, fontWeight: 600, cursor: "pointer" }}>
                              {compareList.find(p => p.id === ingredient.id) ? "비교중 ✓" : "+ 비교"}
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* 비교 탭 */}
        {activeTab === "compare" && (
          <div>
            <div style={{ fontSize: 20, fontWeight: 800, color: "#0f172a", marginBottom: 16 }}>성분 비교</div>
            {compareList.length < 2 ? (
              <div style={{ textAlign: "center", padding: 48, background: "#fff", borderRadius: 16, color: "#94a3b8" }}>
                <div style={{ fontSize: 40, marginBottom: 12 }}>⚖️</div>
                <div style={{ fontSize: 16, fontWeight: 600 }}>비교할 성분을 2개 선택해주세요</div>
                <div style={{ fontSize: 14, marginTop: 4 }}>현재 {compareList.length}개 선택됨</div>
                <button onClick={() => setActiveTab("search")}
                  style={{ marginTop: 16, padding: "10px 24px", borderRadius: 10, border: "none", background: "#10b981", color: "#fff", fontSize: 14, fontWeight: 700, cursor: "pointer" }}>
                  성분 검색하러 가기
                </button>
              </div>
            ) : (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                {compareList.map((item) => {
                  const cfg = SAFETY_CONFIG[item.safety_grade] || SAFETY_CONFIG.safe;
                  return (
                    <div key={item.id} style={{ background: "#fff", borderRadius: 16, padding: 20, boxShadow: "0 1px 3px rgba(0,0,0,0.08)" }}>
                      <div style={{ fontSize: 12, color: "#10b981", fontWeight: 700, marginBottom: 4 }}>{item.category}</div>
                      <div style={{ fontSize: 18, fontWeight: 800, color: "#0f172a", marginBottom: 12 }}>{item.name}</div>
                      {item.kfda_approved && (
                        <span style={{ background: "#dbeafe", color: "#2563eb", fontSize: 11, fontWeight: 700, padding: "3px 8px", borderRadius: 20, display: "inline-block", marginBottom: 10 }}>✓ 식약처 인정</span>
                      )}
                      {item.function && (
                        <div style={{ fontSize: 13, color: "#374151", lineHeight: 1.6, marginBottom: 12 }}>{item.function}</div>
                      )}
                      {item.daily_intake && (
                        <div style={{ padding: 10, background: "#fffbeb", borderRadius: 8, fontSize: 12, color: "#78350f" }}>
                          <strong>상한 섭취량:</strong> {item.daily_intake}
                        </div>
                      )}
                      <div style={{ marginTop: 12, padding: 12, background: cfg.bg, borderRadius: 10, textAlign: "center" }}>
                        <span style={{ color: cfg.color, fontWeight: 800, fontSize: 16 }}>{cfg.icon} {cfg.label}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </main>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        * { box-sizing: border-box; }
      `}</style>
    </div>
  );
}
