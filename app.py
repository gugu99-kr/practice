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
# 스타일 (CSS) - 기존 화려한 디자인 + 요일 배지 추가
# -----------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(99, 102, 241, 0.10), transparent 22%),
        radial-gradient(circle at top right, rgba(56, 189, 248, 0.12), transparent 24%),
        linear-gradient(180deg, #eef4ff 0%, #f8fbff 45%, #f5f7fb 100%);
    color: #0f172a;
}

.block-container {
    max-width: 1180px;
    padding-top: 1.3rem;
}

.app-shell {
    background: rgba(255,255,255,0.42);
    border: 1px solid rgba(255,255,255,0.45);
    backdrop-filter: blur(14px);
    border-radius: 30px;
    padding: 20px;
    box-shadow: 0 14px 40px rgba(15, 23, 42, 0.08);
}

.hero-box {
    background: linear-gradient(135deg, rgba(79, 140, 255, 0.95) 0%, rgba(59, 130, 246, 0.92) 100%);
    padding: 30px;
    border-radius: 28px;
    color: white;
    box-shadow: 0 16px 40px rgba(59, 130, 246, 0.24);
    margin-bottom: 20px;
}

.search-panel {
    background: rgba(255,255,255,0.72);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 24px;
    padding: 20px;
    margin-bottom: 20px;
}

.section-chip {
    display: inline-block;
    font-size: 0.75rem;
    color: #3563e9;
    background: rgba(79, 140, 255, 0.1);
    padding: 4px 12px;
    border-radius: 999px;
    font-weight: 700;
    margin-bottom: 8px;
}

/* 카드 디자인 개선 */
.card {
    background: white;
    border-radius: 26px;
    padding: 24px;
    border: 1px solid rgba(148, 163, 184, 0.12);
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
    min-height: 420px;
}

.card-title { font-size: 1.25rem; font-weight: 800; margin-bottom: 18px; color: #0f172a; }
.label { font-size: 0.82rem; color: #64748b; font-weight: 700; margin-top: 14px; }

/* 요일 배지 */
.day-container { display: flex; gap: 5px; margin-top: 8px; flex-wrap: wrap; }
.day-dot {
    width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;
    border-radius: 50%; background: #f1f5f9; color: #cbd5e1; font-size: 0.8rem; font-weight: 700;
}
.day-dot.active { background: #3b82f6; color: white; }

/* 시간/장소 태그 */
.time-val { font-size: 1.15rem; font-weight: 800; color: #1e293b; margin-top: 4px; }
.place-tag {
    display: inline-block; background: #f0f9ff; color: #0369a1; 
    padding: 4px 10px; border-radius: 8px; font-weight: 700; font-size: 0.85rem; margin-top: 6px;
}

.footer-nav {
    background: #1e293b; color: white; padding: 15px 20px; border-radius: 20px;
    display: flex; justify-content: space-between; margin-top: 30px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------
# 유틸리티 및 데이터 로드
# -----------------------------
DAY_ORDER = ["월", "화", "수", "목", "금", "토", "일"]

def esc(val): return html.escape(str(val))

def pretty_text(val):
    t = str(val).strip() if not pd.isna(val) else "정보 없음"
    return t.replace("+", " · ") if t != "nan" else "정보 없음"

@st.cache_data
def load_data(path):
    for enc in ["cp949", "utf-8-sig", "utf-8"]:
        try:
            df = pd.read_csv(path, encoding=enc)
            df.columns = [c.strip().replace(" ", "") for c in df.columns]
            return df
        except: continue
    return None

def normalize_time(row, prefix):
    start = str(row.get(f"{prefix}쓰레기배출시작시각", row.get(f"{prefix}폐기물배출시작시각", ""))).strip()
    end = str(row.get(f"{prefix}쓰레기배출종료시각", row.get(f"{prefix}폐기물배출종료시각", ""))).strip()
    if not start or start == "nan": return "정보 없음"
    return f"{start} ~ {end}"

# -----------------------------
# 메인 렌더링 함수
# -----------------------------
def render_card(title, emoji, day_raw, time_val, method_val, p_type, p_val):
    # 요일 활성화 체크
    active_days = [d.strip() for d in str(day_raw).replace(",", "·").split("·")]
    days_html = "".join([
        f'<div class="day-dot {"active" if d in active_days else ""}">{d}</div>'
        for d in DAY_ORDER
    ])

    st.markdown(f"""
        <div class="card">
            <div class="card-title">{emoji} {esc(title)}</div>
            
            <div class="label">🗓️ 배출 요일</div>
            <div class="day-container">{days_html}</div>
            
            <div class="label">⏰ 배출 시간</div>
            <div class="time-val">{esc(time_val)}</div>
            
            <div class="label">📝 배출 방법</div>
            <div class="value-text" style="font-weight:600; margin-top:4px;">{esc(method_val)}</div>
            
            <div class="label">📍 배출 장소 유형</div>
            <div class="place-tag">{esc(p_type)}</div>
            
            <div class="label">🏠 상세 장소</div>
            <div class="value-text" style="font-size:0.9rem; color:#64748b;">{esc(p_val)}</div>
        </div>
    """, unsafe_allow_html=True)

# -----------------------------
# 실행 로직
# -----------------------------
DATA_PATH = "생활쓰레기배출정보_서울특별시.csv"
df = load_data(DATA_PATH)

if df is None:
    st.error("데이터 파일을 읽을 수 없습니다. 파일명을 확인해주세요.")
    st.stop()

st.markdown('<div class="app-shell">', unsafe_allow_html=True)

# 헤더
st.markdown('''
<div class="hero-box">
    <div style="font-size:2rem; font-weight:800;">🗑️ 우리 구 쓰레기 배출 도우미</div>
    <div style="opacity:0.9; margin-top:8px;">서울시 자치구별 생활쓰레기 · 음식물 · 재활용품 배출 정보를 한눈에 확인하세요.</div>
</div>
''', unsafe_allow_html=True)

# 검색창
st.markdown('<div class="search-panel"><div class="section-chip">SEARCH</div>', unsafe_allow_html=True)
gu_col = next((c for c in ["시군구명", "자치구명", "구명"] if c in df.columns), df.columns[0])
gu_list = sorted(df[gu_col].unique())

c1, c2 = st.columns([1, 1])
with c1: selected_gu = st.selectbox("자치구 선택", gu_list)
with c2: keyword = st.text_input("키워드 검색 (장소/방법)", placeholder="예: 문전수거, 봉투")
st.markdown('</div>', unsafe_allow_html=True)

# 필터링
filtered = df[df[gu_col] == selected_gu]
if keyword:
    filtered = filtered[filtered.astype(str).apply(lambda x: x.str.contains(keyword, case=False)).any(axis=1)]

if filtered.empty:
    st.warning("일치하는 데이터가 없습니다.")
else:
    row = filtered.iloc[0]
    
    # 데이터 추출
    l_day = pretty_text(row.get("생활쓰레기배출요일", row.get("생활폐기물배출요일", "")))
    l_time = normalize_time(row, "생활")
    l_method = pretty_text(row.get("생활쓰레기배출방법", row.get("생활폐기물배출방법", "")))

    f_day = pretty_text(row.get("음식물쓰레기배출요일", row.get("음식물폐기물배출요일", "")))
    f_time = normalize_time(row, "음식물")
    f_method = pretty_text(row.get("음식물쓰레기배출방법", row.get("음식물폐기물배출방법", "")))

    r_day = pretty_text(row.get("재활용품배출요일", ""))
    r_time = normalize_time(row, "재활용품")
    r_method = pretty_text(row.get("재활용품배출방법", ""))

    p_type = pretty_text(row.get("배출장소유형", "정보 없음"))
    p_val = pretty_text(row.get("배출장소", "정보 없음"))

    # 카드 렌더링
    col_a, col_b, col_c = st.columns(3)
    with col_a: render_card("생활쓰레기", "🛍️", l_day, l_time, l_method, p_type, p_val)
    with col_b: render_card("음식물", "🍎", f_day, f_time, f_method, p_type, p_val)
    with col_c: render_card("재활용품", "♻️", r_day, r_time, r_method, p_type, p_val)

    # 하단 추가 정보 박스
    st.markdown('<div style="margin-top:25px;"></div>', unsafe_allow_html=True)
    i1, i2, i3, i4 = st.columns(4)
    info_items = [
        ("미수거일", row.get("미수거일")),
        ("관리부서", row.get("관리부서명")),
        ("전화번호", row.get("관리부서전화번호")),
        ("데이터기준일", row.get("데이터기준일자"))
    ]
    for col, (lab, val) in zip([i1, i2, i3, i4], info_items):
        with col:
            st.markdown(f'''
            <div style="background:white; padding:15px; border-radius:18px; border:1px solid #e2e8f0; text-align:center;">
                <div style="font-size:0.75rem; color:#64748b; font-weight:700;">{lab}</div>
                <div style="font-size:0.95rem; font-weight:700; margin-top:4px;">{pretty_text(val)}</div>
            </div>
            ''', unsafe_allow_html=True)

# 푸터
st.markdown('''
<div class="footer-nav">
    <div style="font-weight:700;">🗂️ Seoul Waste Helper</div>
    <div style="font-size:0.8rem; opacity:0.8;">공공데이터포털 기준 정보</div>
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # app-shell 닫기
