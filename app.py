import re
import html
import pandas as pd
import streamlit as st

# 1. 페이지 설정
st.set_page_config(
    page_title="우리 구 쓰레기 배출 도우미",
    page_icon="🗑️",
    layout="wide"
)

# -----------------------------
# 스타일 (CSS) - 디자인 개선 버전
# -----------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #f8fbff 0%, #f1f5f9 100%);
    color: #0f172a;
}

.app-shell {
    max-width: 1100px;
    margin: 0 auto;
    padding: 20px;
}

/* 카드 스타일 */
.card {
    background: white;
    border-radius: 24px;
    padding: 24px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    margin-bottom: 20px;
    min-height: 380px;
}

.card-title {
    font-size: 1.3rem;
    font-weight: 800;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* 요일 배지 그룹 */
.day-badge-container {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin: 10px 0 15px 0;
}
.day-badge {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f1f5f9;
    color: #94a3b8;
    border-radius: 50%;
    font-size: 0.85rem;
    font-weight: 700;
    border: 1px solid #e2e8f0;
}
.day-badge.active {
    background: #3b82f6;
    color: white;
    border-color: #2563eb;
}

/* 라벨 및 텍스트 */
.label {
    font-size: 0.8rem;
    color: #64748b;
    font-weight: 700;
    margin-top: 15px;
    text-transform: uppercase;
}
.value-text {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin-top: 4px;
    line-height: 1.5;
}

/* 장소 유형 태그 */
.place-tag {
    display: inline-block;
    background: #eff6ff;
    color: #2563eb;
    padding: 4px 12px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.9rem;
    margin-top: 6px;
}

.time-highlight {
    font-size: 1.2rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.02em;
}

/* 하단 정보 박스 */
.info-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 15px;
    text-align: center;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------
# 유틸리티 함수
# -----------------------------
DAY_ORDER = ["월", "화", "수", "목", "금", "토", "일"]

def esc(val):
    return html.escape(str(val))

def safe_text(val):
    if pd.isna(val) or val is None: return "정보 없음"
    return str(val).strip()

def normalize_time(row, prefix):
    start = safe_text(row.get(f"{prefix}쓰레기배출시작시각", row.get(f"{prefix}폐기물배출시작시각", "")))
    end = safe_text(row.get(f"{prefix}쓰레기배출종료시각", row.get(f"{prefix}폐기물배출종료시각", "")))
    if start == "정보 없음" or not start: return "시간 정보 없음"
    return f"{start} ~ {end}"

@st.cache_data
def load_data(path):
    for enc in ["cp949", "utf-8-sig", "utf-8"]:
        try:
            df = pd.read_csv(path, encoding=enc)
            df.columns = [c.strip().replace(" ", "") for c in df.columns]
            return df
        except: continue
    return None

# -----------------------------
# 카드 렌더링 함수 (핵심 수정 부분)
# -----------------------------
def render_waste_card(title, emoji, day_text, time_text, method_text, place_type, place_val):
    # 요일 활성화 로직
    active_days = [d.strip() for d in day_text.split("·")]
    days_html = "".join([
        f'<div class="day-badge {"active" if d in active_days else ""}">{d}</div>'
        for d in DAY_ORDER
    ])

    st.markdown(f"""
        <div class="card">
            <div class="card-title">{emoji} {esc(title)}</div>
            
            <div class="label">📅 배출 요일</div>
            <div class="day-badge-container">{days_html}</div>
            
            <div class="label">⏰ 배출 시간</div>
            <div class="time-highlight">{esc(time_text)}</div>
            
            <div class="label">📍 배출 장소</div>
            <div class="place-tag">{esc(place_type)}</div>
            <div class="value-text" style="font-size:0.85rem; color:#64748b;">{esc(place_val)}</div>
            
            <div class="label">📝 배출 방법</div>
            <div class="value-text">{esc(method_text)}</div>
        </div>
    """, unsafe_allow_html=True)

# -----------------------------
# 데이터 로드 및 실행
# -----------------------------
DATA_PATH = "생활쓰레기배출정보_서울특별시.csv"
df = load_data(DATA_PATH)

if df is None:
    st.error("데이터 파일을 찾을 수 없습니다. 파일명을 확인해주세요.")
    st.stop()

st.markdown('<div class="app-shell">', unsafe_allow_html=True)

# 검색 섹션
gu_list = sorted(df["시군구명"].unique()) if "시군구명" in df.columns else sorted(df.iloc[:,0].unique())
selected_gu = st.selectbox("어느 지역의 배출 정보를 찾으시나요?", gu_list)

filtered = df[df.iloc[:, 0] == selected_gu]

if not filtered.empty:
    row = filtered.iloc[0]
    
    # 데이터 매핑 (접두어 기준)
    # 1. 생활쓰레기
    l_day = safe_text(row.get("생활쓰레기배출요일", row.get("생활폐기물배출요일", "정보 없음")))
    l_time = normalize_time(row, "생활")
    l_method = safe_text(row.get("생활쓰레기배출방법", row.get("생활폐기물배출방법", "정보 없음")))
    
    # 2. 음식물
    f_day = safe_text(row.get("음식물쓰레기배출요일", row.get("음식물폐기물배출요일", "정보 없음")))
    f_time = normalize_time(row, "음식물")
    f_method = safe_text(row.get("음식물쓰레기배출방법", row.get("음식물폐기물배출방법", "정보 없음")))
    
    # 3. 재활용
    r_day = safe_text(row.get("재활용품배출요일", "정보 없음"))
    r_time = normalize_time(row, "재활용품")
    r_method = safe_text(row.get("재활용품배출방법", "정보 없음"))
    
    p_type = safe_text(row.get("배출장소유형", "정보 없음"))
    p_val = safe_text(row.get("배출장소", "정보 없음"))

    # 카드 출력
    col1, col2, col3 = st.columns(3)
    with col1: render_waste_card("생활쓰레기", "🛍️", l_day, l_time, l_method, p_type, p_val)
    with col2: render_waste_card("음식물", "🍎", f_day, f_time, f_method, p_type, p_val)
    with col3: render_waste_card("재활용품", "♻️", r_day, r_time, r_method, p_type, p_val)

    # 하단 추가 정보
    st.write("---")
    a1, a2, a3 = st.columns(3)
    with a1: st.markdown(f'<div class="info-box"><div class="label">미수거일</div><div class="value-text">{safe_text(row.get("미수거일"))}</div></div>', unsafe_allow_html=True)
    with a2: st.markdown(f'<div class="info-box"><div class="label">관리부서</div><div class="value-text">{safe_text(row.get("관리부서명"))}</div></div>', unsafe_allow_html=True)
    with a3: st.markdown(f'<div class="info-box"><div class="label">문의처</div><div class="value-text">{safe_text(row.get("관리부서전화번호"))}</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
