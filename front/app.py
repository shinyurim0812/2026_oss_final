import os

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000")

BUDGET_OPTIONS = ["3000원 이하", "5000원 이하", "8000원 이하", "상관없음"]
TIME_OPTIONS = ["10분 이내", "20분 이내", "30분 이내", "시간 상관없음"]
INGREDIENT_OPTIONS = ["밥", "계란", "김치", "참치", "두부", "닭가슴살", "라면", "채소", "치즈", "빵"]
RANK_LABELS = ["1순위", "2순위", "3순위"]


st.set_page_config(
    page_title="혼밥메이트",
    page_icon="🍚",
    layout="centered",
)

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #666;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }
    .author {
        text-align: center;
        color: #8a4b08;
        font-size: 0.95rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }
    .result-card {
        border: 1px solid #eadfce;
        border-radius: 14px;
        padding: 1.2rem;
        margin: 1rem 0;
        background: #fffaf2;
        box-shadow: 0 2px 10px rgba(90, 60, 20, 0.06);
    }
    .card-top {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 0.8rem;
        margin-bottom: 0.85rem;
    }
    .rank {
        border-radius: 999px;
        padding: 0.35rem 0.7rem;
        background: #ffe8bd;
        color: #7a4104;
        display: inline-block;
        font-size: 0.95rem;
        font-weight: 800;
    }
    .menu-name {
        font-size: 1.55rem;
        font-weight: 800;
        margin: 0.55rem 0 0;
    }
    .score-badge {
        flex: 0 0 auto;
        border-radius: 999px;
        padding: 0.45rem 0.85rem;
        background: #fff0cf;
        border: 1px solid #f3cf8d;
        color: #7a4104;
        font-weight: 800;
        white-space: nowrap;
    }
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.55rem;
        margin: 0.8rem 0 0.9rem;
    }
    .metric {
        border-radius: 10px;
        background: #ffffff;
        border: 1px solid #f0dfc6;
        padding: 0.7rem 0.6rem;
        text-align: center;
    }
    .metric-label {
        color: #85684d;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .metric-value {
        color: #2f261c;
        font-size: 1.02rem;
        font-weight: 800;
    }
    .section-block {
        border-top: 1px solid #f0dfc6;
        padding-top: 0.75rem;
        margin-top: 0.75rem;
    }
    .meta {
        color: #444;
        line-height: 1.65;
    }
    .score-summary {
        padding: 1rem 1.1rem;
        border-radius: 12px;
        background: #f7fbff;
        border: 1px solid #cfe4ff;
        color: #24384f;
        line-height: 1.75;
        margin: 1.1rem 0 0.5rem;
    }
    .score-summary-title {
        font-weight: 800;
        margin-bottom: 0.45rem;
    }
    .api-note {
        padding: 0.8rem 1rem;
        border-radius: 10px;
        background: #eef9f0;
        color: #236534;
        border: 1px solid #c9ebd0;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="author">2023204093 신유림</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🍚 혼밥메이트</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">예산, 시간, 냉장고 재료로 오늘의 자취 식단을 추천해드려요.</div>',
    unsafe_allow_html=True,
)

with st.container():
    st.subheader("📝 오늘의 조건을 알려주세요")
    budget = st.selectbox(
        "💰 한 끼 예산",
        BUDGET_OPTIONS,
        index=None,
        placeholder="한 끼 예산을 선택하세요",
    )
    max_time = st.selectbox(
        "⏱️ 조리 가능 시간",
        TIME_OPTIONS,
        index=None,
        placeholder="조리 가능 시간을 선택하세요",
    )
    ingredients = st.multiselect("🥬 냉장고에 있는 재료", INGREDIENT_OPTIONS)

st.markdown("#### 📌 선택한 조건 요약")
summary_budget = budget if budget else "아직 선택하지 않음"
summary_time = max_time if max_time else "아직 선택하지 않음"
summary_ingredients = ", ".join(ingredients) if ingredients else "선택한 재료 없음"
st.caption(f"💰 예산: {summary_budget} | ⏱️ 시간: {summary_time} | 🥬 재료: {summary_ingredients}")

recommend_button = st.button("🍽️ 식단 추천받기", type="primary", use_container_width=True)

if recommend_button:
    if budget is None or max_time is None:
        st.warning("예산과 조리 가능 시간을 먼저 선택해주세요.")
        st.stop()

    payload = {
        "budget": budget,
        "max_time": max_time,
        "ingredients": ingredients,
    }

    try:
        response = requests.post(f"{API_URL}/recommend", json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as error:
        st.error("FastAPI 서버에 연결할 수 없습니다. 백엔드 컨테이너가 실행 중인지 확인해주세요.")
        st.caption(f"오류 내용: {error}")
    else:
        st.subheader("🍱 오늘의 추천 메뉴 TOP 3")
        score_summaries = []

        for index, menu in enumerate(data["recommendations"]):
            matched = ", ".join(menu["matched_ingredients"]) if menu["matched_ingredients"] else "없음"
            missing = ", ".join(menu["missing_ingredients"]) if menu["missing_ingredients"] else "없음"
            all_ingredients = ", ".join(menu["ingredients"])
            score_detail = menu["score_detail"]
            score_text = (
                f"예산 {score_detail['budget_score']}점 + "
                f"시간 {score_detail['time_score']}점 + "
                f"재료 {score_detail['ingredient_score']}점 = "
                f"총 {score_detail['total_score']}점"
            )
            score_summaries.append(
                f"{RANK_LABELS[index]} {menu['name']}은 예산 {score_detail['budget_score']}점, "
                f"시간 {score_detail['time_score']}점, 재료 {score_detail['ingredient_score']}점을 받아 "
                f"총 {score_detail['total_score']}점입니다"
            )

            st.markdown(
                f"""
                <div class="result-card">
                    <div class="card-top">
                        <div>
                            <div class="rank">🏆 {RANK_LABELS[index]}</div>
                            <div class="menu-name">{menu["name"]}</div>
                        </div>
                        <div class="score-badge">총 {menu["score"]}점</div>
                    </div>
                    <div class="metric-grid">
                        <div class="metric">
                            <div class="metric-label">💰 예상 비용</div>
                            <div class="metric-value">{menu["cost"]:,}원</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">⏱️ 조리 시간</div>
                            <div class="metric-value">{menu["time"]}분</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">⭐ 난이도</div>
                            <div class="metric-value">{menu["difficulty"]}</div>
                        </div>
                    </div>
                    <div class="section-block meta">
                        📊 <strong>점수 계산</strong>: {score_text}
                    </div>
                    <div class="section-block meta">
                        🧂 <strong>전체 필요 재료</strong>: {all_ingredients}<br>
                        ✅ <strong>있는 재료</strong>: {matched}<br>
                        🛒 <strong>추가로 필요한 재료</strong>: {missing}
                    </div>
                    <div class="section-block meta">
                        💡 <strong>추천 이유</strong><br>
                        {menu["reason"]}<br>
                        👩‍🍳 <strong>팁</strong><br>
                        {menu["tip"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div class="score-summary">
                <div class="score-summary-title">📊 점수 산출 요약</div>
                {'. '.join(score_summaries)}. 점수는 FastAPI 백엔드에서 예산 조건, 조리 시간 조건,
                보유 재료 일치 수를 합산해 계산했습니다.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="api-note">✅ FastAPI <strong>POST /recommend</strong> 응답으로 받은 추천 결과입니다.</div>',
            unsafe_allow_html=True,
        )
else:
    st.info("조건을 고른 뒤 🍽️ 식단 추천받기 버튼을 눌러주세요.")
