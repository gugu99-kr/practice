import re
import html
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="우리 구 쓰레기 배출 도우미",
    page_icon="🗑️",
    layout="wide"
)

# -----------------------------
# 스타일
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
    padding-bottom: 2.5rem;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fbff 0%, #eef5ff 100%);
    border-right: 1px solid rgba(148, 163, 184, 0.18);
}

div[data-testid="stSelectbox"] > div,
div[data-testid="stTextInput"] > div {
    border-radius: 16px !important;
}

.app-shell {
    background: rgba(255,255,255,0.42);
    border: 1px solid rgba(255,255,255,0.45);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 30px;
    padding: 18px;
    box-shadow: 0 14px 40px rgba(15, 23, 42, 0.08);
    margin-bottom: 18px;
}

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    margin-bottom: 16px;
}

.app-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(79, 140, 255, 0.10);
    color: #3563e9;
    border: 1px solid rgba(79, 140, 255, 0.18);
    padding: 8px 14px;
    border-radius: 999px;
    font-size: 0.9rem;
    font-weight: 700;
}

.top-status {
    background: rgba(255,255,255,0.8);
    border: 1px solid rgba(15,23,42,0.05);
    border-radius: 999px;
    padding: 8px 14px;
    font-size: 0.85rem;
    color: #475569;
    font-weight: 600;
}

.hero-box {
    background:
        linear-gradient(135deg, rgba(79, 140, 255, 0.95) 0%, rgba(96, 165, 250, 0.92) 45%, rgba(59, 130, 246, 0.92) 100%);
    padding: 30px 28px;
    border-radius: 28px;
    color: white;
    box-shadow: 0 16px 40px rgba(59, 130, 246, 0.24);
    position: relative;
    overflow: hidden;
    margin-bottom: 18px;
}

.hero-box::after {
    content: "";
    position: absolute;
    right: -40px;
    top: -40px;
    width: 180px;
    height: 180px;
    background: rgba(255,255,255,0.10);
    border-radius: 50%;
}

.hero-title {
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 0.45rem;
    letter-spacing: -0.02em;
    position: relative;
    z-index: 2;
}

.hero-sub {
    font-size: 1rem;
    opacity: 0.96;
    line-height: 1.6;
    position: relative;
    z-index: 2;
}

.search-panel {
    background: rgba(255,255,255,0.72);
    border: 1px solid rgba(148, 163, 184, 0.16);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 24px;
    padding: 18px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
    margin-bottom: 18px;
}

.section-chip {
    display: inline-block;
    font-size: 0.82rem;
    color: #3563e9;
    background: rgba(79, 140, 255, 0.10);
    border: 1px solid rgba(79, 140, 255, 0.14);
    padding: 6px 12px;
    border-radius: 999px;
    font-weight: 700;
    margin-bottom: 10px;
}

.section-title {
    font-size: 1.3rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 2px;
}

.section-sub {
    color: #64748b;
    font-size: 0.95rem;
    margin-bottom: 10px;
}

.card {
    background: rgba(255,255,255,0.82);
    border-radius: 26px;
    padding: 22px 20px;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
    border: 1px solid rgba(148, 163, 184, 0.12);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    min-height: 335px;
    transition: transform 0.18s ease;
}
.card:hover {
    transform: translateY(-2px);
}
.card-title {
    font-size: 1.18rem;
    font-weight: 800;
    margin-bottom: 14px;
    color: #0f172a;
}
.label {
    font-size: 0.82rem;
    color: #64748b;
    margin-top: 12px;
    margin-bottom: 3px;
    font-weight: 600;
}
.value {
    font-size: 1rem;
    font-weight: 700;
    color: #111827;
    line-height: 1.65;
    word-break: keep-all;
    overflow-wrap: break-word;
}

.info-grid-box {
    background: rgba(255,255,255,0.72);
    border-radius: 24px;
    padding: 18px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    border: 1px solid rgba(148, 163, 184, 0.14);
    margin-top: 10px;
}

.small-box {
    background: linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(248,250,252,0.95) 100%);
    border-radius: 20px;
    padding: 16px 16px;
    border: 1px solid rgba(148, 163, 184, 0.12);
    min-height: 108px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
}

.footer-box {
    background: rgba(255,255,255,0.82);
    border-radius: 24px;
    padding: 20px;
    box-shadow: 0 10px 24px rgba(15,23,42,0.05);
    border: 1px solid rgba(148,163,184,0.12);
    margin-top: 18px;
}
.note-text {
    color: #475569;
    font-size: 0.95rem;
    line-height: 1.7;
}

.bottom-nav {
    margin-top: 18px;
    padding: 14px 18px;
    border-radius: 22px;
    background: rgba(15, 23, 42, 0.92);
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 14px 28px rgba(15, 23, 42, 0.18);
}
.bottom-nav-left {
    font-weight: 700;
    font-size: 0.95rem;
}
.bottom-nav-right {
    font-size: 0.84rem;
    color: rgba(255,255,255,0.78);
}

div[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
}

@media (max-width: 900px) {
    .hero-title {
        font-size: 1.7rem;
    }
    .card {
        min-height: auto;
    }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

DAY_ORDER = ["월", "화", "수", "목", "금", "토", "일"]

# -----------------------------
# 유틸 함수
# -----------------------------
def safe_text(val):
    if val is None or pd.isna(val):
        return "정보 없음"
    text = str(val).strip()
    if text == "" or text.lower() == "nan":
        return "정보 없음"
    return text

def pretty_text(text):
    text = safe_text(text)
    if text == "정보 없음":
        return text
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace(" ,", ",")
    text = text.replace("+", " · ")
    text = text.replace("건물앞", "건물 앞")
    text = text.replace("점포앞", "점포 앞")
    text = text.replace("대문앞", "대문 앞")
    return text

def find_column(df, candidates):
    normalized = {str(col).strip(): col for col in df.columns}
    for cand in candidates:
        if cand in normalized:
            return normalized[cand]
    return None

def normalize_day_text(text):
    if pd.isna(text):
        return "정보 없음"
    s = str(text).strip()
    if not s:
        return "정보 없음"
    s = s.replace(" ", "")
    tokens = re.split(r"[+,/·ㆍ\s]+", s)
    tokens = [t for t in tokens if t]

    found = []
    for day in DAY_ORDER:
        if day in tokens or day in s:
            found.append(day)

    if found:
        return " · ".join(found)
    return pretty_text(s)

def normalize_time_piece(value):
    text = safe_text(value)
    if text == "정보 없음":
        return text
    text = str(text).strip()

    if re.fullmatch(r"\d{4}", text):
        return f"{text[:2]}:{text[2:]}"
    if re.fullmatch(r"\d{1,2}", text):
        return f"{int(text):02d}:00"
    return text

def normalize_time_text(start, end):
    start = normalize_time_piece(start)
    end = normalize_time_piece(end)

    if start == "정보 없음" and end == "정보 없음":
        return "정보 없음"
    if start != "정보 없음" and end != "정보 없음":
        return f"{start} ~ {end}"
    return start if start != "정보 없음" else end

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    encodings = ["cp949", "utf-8-sig", "utf-8", "euc-kr"]

    last_error = None
    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc)
            df.columns = [str(col).strip() for col in df.columns]
            return df
        except Exception as e:
            last_error = e

    raise ValueError(f"CSV 파일을 읽지 못했습니다. 오류: {last_error}")

def extract_info(row, kind="생활"):
    kind_map = {
        "생활": {
            "method": ["생활쓰레기배출방법", "생활폐기물배출방법"],
            "day": ["생활쓰레기배출요일", "생활폐기물배출요일"],
            "start": ["생활쓰레기배출시작시각", "생활쓰레기배출시작시간"],
            "end": ["생활쓰레기배출종료시각", "생활쓰레기배출종료시간"],
        },
        "음식물": {
            "method": ["음식물쓰레기배출방법", "음식물폐기물배출방법"],
            "day": ["음식물쓰레기배출요일", "음식물폐기물배출요일"],
            "start": ["음식물쓰레기배출시작시각", "음식물쓰레기배출시작시간"],
            "end": ["음식물쓰레기배출종료시각", "음식물쓰레기배출종료시간"],
        },
        "재활용": {
            "method": ["재활용품배출방법"],
            "day": ["재활용품배출요일"],
            "start": ["재활용품배출시작시각", "재활용품배출시작시간"],
            "end": ["재활용품배출종료시각", "재활용품배출종료시간"],
        },
    }

    selected = kind_map[kind]

    method_col = next((c for c in selected["method"] if c in row.index), None)
    day_col = next((c for c in selected["day"] if c in row.index), None)
    start_col = next((c for c in selected["start"] if c in row.index), None)
    end_col = next((c for c in selected["end"] if c in row.index), None)

    method = pretty_text(row[method_col]) if method_col else "정보 없음"
    day_raw = row[day_col] if day_col else None
    start_raw = row[start_col] if start_col else None
    end_raw = row[end_col] if end_col else None

    day = normalize_day_text(day_raw)
    time_text = normalize_time_text(start_raw, end_raw)

    return {
        "method": method,
        "day": day,
        "time": time_text
    }

def esc(val):
    return html.escape(str(val))

def render_card(title, emoji, info, place_type, place):
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">{emoji} {esc(title)}</div>

            <div class="label">배출요일</div>
            <div class="value">{esc(info["day"])}</div>

            <div class="label">배출시간</div>
            <div class="value">{esc(info["time"])}</div>

            <div class="label">배출방법</div>
            <div class="value">{esc(info["method"])}</div>

            <div class="label">배출장소 유형</div>
            <div class="value">{esc(place_type)}</div>

            <div class="label">배출장소</div>
            <div class="value">{esc(place)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# 데이터 로드
# -----------------------------
DATA_PATH = "생활쓰레기배출정보_서울특별시.csv"

try:
    df = load_data(DATA_PATH)
except Exception as e:
    st.error("데이터 파일을 불러오지 못했습니다.")
    st.exception(e)
    st.stop()

gu_col = find_column(df, ["시군구명", "자치구명", "구명"])
sido_col = find_column(df, ["시도명"])
place_type_col = find_column(df, ["배출장소유형"])
place_col = find_column(df, ["배출장소"])
nocollect_col = find_column(df, ["미수거일"])
dept_col = find_column(df, ["관리부서명"])
phone_col = find_column(df, ["관리부서전화번호"])
date_col = find_column(df, ["데이터기준일자"])
updated_col = find_column(df, ["최종수정시점"])

if gu_col is None:
    st.error("`시군구명` 컬럼을 찾지 못했습니다. CSV 컬럼명을 확인해주세요.")
    st.write("현재 컬럼 목록:", list(df.columns))
    st.stop()

if sido_col and sido_col in df.columns:
    df = df[df[sido_col].astype(str).str.contains("서울", na=False)].copy()

gu_list = sorted(df[gu_col].dropna().astype(str).str.strip().unique().tolist())

if not gu_list:
    st.error("구 목록을 불러오지 못했습니다. 데이터 내용을 확인해주세요.")
    st.stop()

# -----------------------------
# 앱 셸
# -----------------------------
st.markdown('<div class="app-shell">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="topbar">
        <div class="app-badge">📱 Seoul Waste Helper</div>
        <div class="top-status">실시간 조회형 안내 화면</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero-box">
        <div class="hero-title">🗑️ 우리 구 쓰레기 배출 도우미</div>
        <div class="hero-sub">
            서울시 자치구별 생활쓰레기 · 음식물쓰레기 · 재활용품 배출 요일과 방법을
            앱처럼 쉽고 빠르게 확인해보세요.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="search-panel">
        <div class="section-chip">SEARCH PANEL</div>
        <div class="section-title">배출 정보 검색</div>
        <div class="section-sub">자치구와 키워드를 선택해서 필요한 배출 규칙을 찾아보세요.</div>
    </div>
    """,
    unsafe_allow_html=True
)

filter_col1, filter_col2, filter_col3 = st.columns([1.2, 1.2, 0.8])

with filter_col1:
    selected_gu = st.selectbox("자치구 선택", gu_list)

with filter_col2:
    keyword = st.text_input(
        "배출장소/방법 키워드 검색",
        placeholder="예: 문전수거, 거점배출, 클린하우스"
    )

with filter_col3:
    show_raw = st.checkbox("원본 데이터 보기", value=False)

filtered = df[df[gu_col].astype(str).str.strip() == selected_gu].copy()

if keyword:
    keyword = keyword.strip()
    search_cols = [c for c in [place_col, place_type_col] if c is not None]
    waste_method_cols = [
        c for c in [
            "생활쓰레기배출방법",
            "음식물쓰레기배출방법",
            "재활용품배출방법",
            "생활폐기물배출방법",
            "음식물폐기물배출방법"
        ] if c in filtered.columns
    ]
    search_cols += waste_method_cols

    if search_cols:
        mask = filtered[search_cols].astype(str).apply(
            lambda row: row.str.contains(keyword, case=False, na=False)
        ).any(axis=1)
        filtered = filtered[mask].copy()

st.markdown(
    f"""
    <div style="margin-top:14px; margin-bottom:8px;">
        <div class="section-chip">RESULT</div>
        <div class="section-title">📍 {esc(selected_gu)} 배출 정보</div>
        <div class="section-sub">선택한 자치구 기준 대표 배출 정보를 표시합니다.</div>
    </div>
    """,
    unsafe_allow_html=True
)

if filtered.empty:
    st.warning("검색 조건에 맞는 데이터가 없습니다.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

row = filtered.iloc[0]

place_type = pretty_text(row[place_type_col]) if place_type_col else "정보 없음"
place = pretty_text(row[place_col]) if place_col else "정보 없음"

life_info = extract_info(row, "생활")
food_info = extract_info(row, "음식물")
recycle_info = extract_info(row, "재활용")

col1, col2, col3 = st.columns(3)

with col1:
    render_card("생활쓰레기", "🛍️", life_info, place_type, place)
with col2:
    render_card("음식물쓰레기", "🍎", food_info, place_type, place)
with col3:
    render_card("재활용품", "♻️", recycle_info, place_type, place)

st.markdown('<div class="info-grid-box">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="section-chip">DETAIL</div>
    <div class="section-title">추가 안내 정보</div>
    <div class="section-sub">수거 제외일, 담당부서, 연락처, 데이터 기준일을 확인할 수 있습니다.</div>
    """,
    unsafe_allow_html=True
)

col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    st.markdown(
        f"""
        <div class="small-box">
            <div class="label">미수거일</div>
            <div class="value">{esc(pretty_text(row[nocollect_col]) if nocollect_col else "정보 없음")}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_b:
    st.markdown(
        f"""
        <div class="small-box">
            <div class="label">관리부서</div>
            <div class="value">{esc(pretty_text(row[dept_col]) if dept_col else "정보 없음")}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_c:
    st.markdown(
        f"""
        <div class="small-box">
            <div class="label">전화번호</div>
            <div class="value">{esc(pretty_text(row[phone_col]) if phone_col else "정보 없음")}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_d:
    base_date = pretty_text(row[date_col]) if date_col else "정보 없음"
    updated_date = pretty_text(row[updated_col]) if updated_col else "정보 없음"
    st.markdown(
        f"""
        <div class="small-box">
            <div class="label">기준일 / 수정일</div>
            <div class="value">{esc(base_date)}<br>{esc(updated_date)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="footer-box">
        <div class="section-chip">NOTICE</div>
        <div class="section-title">이용 안내</div>
        <div class="note-text">
            자치구마다 배출요일, 배출시간, 배출방법이 다를 수 있습니다.<br>
            실제 배출 전에는 담당 부서 또는 자치구 공식 안내를 함께 확인해주세요.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if show_raw:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("원본 데이터")
    st.dataframe(filtered, use_container_width=True)

st.markdown(
    """
    <div class="bottom-nav">
        <div class="bottom-nav-left">🗂️ 우리 구 쓰레기 배출 도우미</div>
        <div class="bottom-nav-right">서울시 자치구 생활폐기물 안내</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)
