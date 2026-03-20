import re
from datetime import datetime
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
.stApp {
    background:
        radial-gradient(circle at top left, rgba(99, 102, 241, 0.08), transparent 22%),
        radial-gradient(circle at top right, rgba(56, 189, 248, 0.10), transparent 24%),
        linear-gradient(180deg, #eaf2ff 0%, #f7fbff 42%, #f4f7fb 100%);
}

.block-container {
    max-width: 1180px;
    padding-top: 1.3rem;
    padding-bottom: 2.2rem;
}

/* 상단 히어로 */
.hero-box {
    background:
        linear-gradient(135deg, rgba(79, 140, 255, 0.95) 0%, rgba(110, 177, 255, 0.92) 55%, rgba(61, 132, 247, 0.92) 100%);
    padding: 30px 32px;
    border-radius: 30px;
    color: white;
    margin-bottom: 20px;
    box-shadow: 0 16px 36px rgba(79, 140, 255, 0.22);
    position: relative;
    overflow: hidden;
}

.hero-box::after {
    content: "";
    position: absolute;
    right: -30px;
    top: -30px;
    width: 170px;
    height: 170px;
    background: rgba(255,255,255,0.10);
    border-radius: 50%;
}

.hero-title {
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 0.45rem;
    position: relative;
    z-index: 1;
}

.hero-sub {
    font-size: 1rem;
    opacity: 0.96;
    line-height: 1.65;
    position: relative;
    z-index: 1;
}

/* 검색 패널 */
.search-box {
    background: rgba(255,255,255,0.74);
    border: 1px solid rgba(148,163,184,0.14);
    border-radius: 26px;
    padding: 18px;
    margin-bottom: 18px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}

.section-title {
    font-size: 1.15rem;
    font-weight: 800;
    margin-bottom: 10px;
    color: #0f172a;
}

/* 오늘 정보 패널 */
.today-box {
    background: rgba(255,255,255,0.80);
    border: 1px solid rgba(148,163,184,0.14);
    border-radius: 24px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}

.today-title {
    font-size: 1.08rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 4px;
}

.today-sub {
    font-size: 0.95rem;
    color: #64748b;
}

/* 쓰레기 정보 카드 */
div[data-testid="stVerticalBlock"] div[data-testid="stContainer"] {
    border-radius: 24px;
}

.waste-card {
    background: rgba(255,255,255,0.88);
    border: 1px solid rgba(148,163,184,0.12);
    border-radius: 26px;
    padding: 22px 20px;
    box-shadow: 0 12px 26px rgba(15, 23, 42, 0.06);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    min-height: 360px;
}

.waste-card-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 4px;
}

.waste-card-sub {
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 14px;
}

.waste-label {
    font-size: 0.84rem;
    color: #64748b;
    font-weight: 700;
    margin-top: 14px;
    margin-bottom: 4px;
}

.waste-value {
    font-size: 1rem;
    color: #111827;
    font-weight: 600;
    line-height: 1.65;
    word-break: keep-all;
    overflow-wrap: break-word;
    white-space: pre-wrap;
}

.badge-ok {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 999px;
    background: rgba(34, 197, 94, 0.12);
    color: #166534;
    font-size: 0.88rem;
    font-weight: 800;
    border: 1px solid rgba(34, 197, 94, 0.16);
    margin-bottom: 6px;
}

.badge-no {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 999px;
    background: rgba(245, 158, 11, 0.14);
    color: #92400e;
    font-size: 0.88rem;
    font-weight: 800;
    border: 1px solid rgba(245, 158, 11, 0.18);
    margin-bottom: 6px;
}

.badge-unknown {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 999px;
    background: rgba(148, 163, 184, 0.16);
    color: #475569;
    font-size: 0.88rem;
    font-weight: 800;
    border: 1px solid rgba(148, 163, 184, 0.16);
    margin-bottom: 6px;
}

/* 아이폰 날씨앱 느낌 하단 카드 */
.glass-wrap {
    margin-top: 18px;
    margin-bottom: 8px;
}

.glass-card {
    background: linear-gradient(
        180deg,
        rgba(255,255,255,0.45) 0%,
        rgba(255,255,255,0.22) 100%
    );
    border: 1px solid rgba(255,255,255,0.34);
    border-radius: 26px;
    padding: 18px;
    min-height: 128px;
    box-shadow:
        0 10px 30px rgba(15, 23, 42, 0.08),
        inset 0 1px 0 rgba(255,255,255,0.45);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
}

.glass-label {
    font-size: 0.78rem;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    color: #64748b;
    font-weight: 800;
    margin-bottom: 10px;
}

.glass-value {
    font-size: 1.05rem;
    line-height: 1.45;
    color: #0f172a;
    font-weight: 700;
    word-break: keep-all;
    overflow-wrap: break-word;
}

.glass-sub {
    font-size: 0.88rem;
    color: #64748b;
    margin-top: 8px;
    line-height: 1.45;
}

/* 하단 안내 */
.footer-box {
    background: rgba(255,255,255,0.82);
    border-radius: 24px;
    padding: 20px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.05);
    border: 1px solid rgba(0,0,0,0.04);
    margin-top: 18px;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}

.note-text {
    color: #475467;
    font-size: 0.95rem;
    line-height: 1.7;
}

/* input 모양 */
div[data-testid="stSelectbox"] > div {
    border-radius: 16px !important;
}

@media (max-width: 900px) {
    .hero-title {
        font-size: 1.7rem;
    }
    .waste-card {
        min-height: auto;
    }
    .glass-card {
        min-height: 110px;
    }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

DAY_ORDER = ["월", "화", "수", "목", "금", "토", "일"]
DAY_TO_INDEX = {
    "월": 0,
    "화": 1,
    "수": 2,
    "목": 3,
    "금": 4,
    "토": 5,
    "일": 6,
}
INDEX_TO_DAY = {v: k for k, v in DAY_TO_INDEX.items()}


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


def pretty_text(val):
    text = safe_text(val)
    if text == "정보 없음":
        return text

    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace(" ,", ",")
    text = text.replace("+", " · ")
    text = text.replace("건물앞", "건물 앞")
    text = text.replace("점포앞", "점포 앞")
    text = text.replace("대문앞", "대문 앞")
    return text


def normalize_day_text(val):
    text = safe_text(val)
    if text == "정보 없음":
        return text

    raw = text.replace(" ", "")
    tokens = re.split(r"[+,/·ㆍ\\s]+", raw)
    tokens = [t for t in tokens if t]

    found = []
    for d in DAY_ORDER:
        if d in tokens or d in raw:
            found.append(d)

    if found:
        return " · ".join(found)

    return pretty_text(text)


def extract_day_list(val):
    text = safe_text(val)
    if text == "정보 없음":
        return []

    raw = text.replace(" ", "")
    tokens = re.split(r"[+,/·ㆍ\\s]+", raw)
    tokens = [t for t in tokens if t]

    found = []
    for d in DAY_ORDER:
        if d in tokens or d in raw:
            found.append(d)

    return found


def normalize_time_piece(val):
    text = safe_text(val)
    if text == "정보 없음":
        return text

    if re.fullmatch(r"\d{4}", text):
        return f"{text[:2]}:{text[2:]}"
    if re.fullmatch(r"\d{1,2}", text):
        return f"{int(text):02d}:00"

    return text


def normalize_time_text(start, end):
    s = normalize_time_piece(start)
    e = normalize_time_piece(end)

    if s == "정보 없음" and e == "정보 없음":
        return "정보 없음"
    if s != "정보 없음" and e != "정보 없음":
        return f"{s} ~ {e}"
    return s if s != "정보 없음" else e


def find_column(df, candidates):
    normalized = {str(col).strip(): col for col in df.columns}
    for cand in candidates:
        if cand in normalized:
            return normalized[cand]
    return None


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
            "title": "생활쓰레기",
            "emoji": "🛍️",
            "method": ["생활쓰레기배출방법", "생활폐기물배출방법"],
            "day": ["생활쓰레기배출요일", "생활폐기물배출요일"],
            "start": ["생활쓰레기배출시작시각", "생활쓰레기배출시작시간"],
            "end": ["생활쓰레기배출종료시각", "생활쓰레기배출종료시간"],
        },
        "음식물": {
            "title": "음식물",
            "emoji": "🍎",
            "method": ["음식물쓰레기배출방법", "음식물폐기물배출방법"],
            "day": ["음식물쓰레기배출요일", "음식물폐기물배출요일"],
            "start": ["음식물쓰레기배출시작시각", "음식물쓰레기배출시작시간"],
            "end": ["음식물쓰레기배출종료시각", "음식물쓰레기배출종료시간"],
        },
        "재활용": {
            "title": "재활용품",
            "emoji": "♻️",
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

    raw_day = row[day_col] if day_col else None

    return {
        "title": selected["title"],
        "emoji": selected["emoji"],
        "method": pretty_text(row[method_col]) if method_col else "정보 없음",
        "day": normalize_day_text(raw_day),
        "day_list": extract_day_list(raw_day),
        "time": normalize_time_text(
            row[start_col] if start_col else None,
            row[end_col] if end_col else None
        )
    }


def is_collectable_today(day_list):
    if not day_list:
        return None
    today_idx = datetime.now().weekday()
    today_day = INDEX_TO_DAY[today_idx]
    return today_day in day_list


def render_status_badge(flag):
    if flag is True:
        st.markdown('<div class="badge-ok">오늘 배출 가능</div>', unsafe_allow_html=True)
    elif flag is False:
        st.markdown('<div class="badge-no">오늘 배출일 아님</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge-unknown">확인 불가</div>', unsafe_allow_html=True)


def render_native_card(title, emoji, info, place_type, place):
    today_flag = is_collectable_today(info["day_list"])

    st.markdown('<div class="waste-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="waste-card-title">{emoji} {title}</div>', unsafe_allow_html=True)
    st.markdown('<div class="waste-card-sub">배출 규칙 안내</div>', unsafe_allow_html=True)

    render_status_badge(today_flag)

    st.markdown('<div class="waste-label">🗓️ 배출 요일</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="waste-value">{info["day"]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="waste-label">⏰ 배출 시간</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="waste-value">{info["time"]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="waste-label">📝 배출 방법</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="waste-value">{info["method"]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="waste-label">📍 배출 장소 유형</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="waste-value">{place_type}</div>', unsafe_allow_html=True)

    st.markdown('<div class="waste-label">🏠 상세 장소</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="waste-value">{place}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_glass_info_card(label, value, sub_text=""):
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="glass-label">{label}</div>
            <div class="glass-value">{value}</div>
            <div class="glass-sub">{sub_text}</div>
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
    st.error("`시군구명` 컬럼을 찾지 못했습니다.")
    st.write("현재 컬럼 목록:", list(df.columns))
    st.stop()

if sido_col and sido_col in df.columns:
    df = df[df[sido_col].astype(str).str.contains("서울", na=False)].copy()

gu_list = sorted(df[gu_col].dropna().astype(str).str.strip().unique().tolist())

if not gu_list:
    st.error("구 목록을 불러오지 못했습니다.")
    st.stop()

# -----------------------------
# 헤더
# -----------------------------
st.markdown(
    """
    <div class="hero-box">
        <div class="hero-title">🗑️ 우리 구 쓰레기 배출 도우미</div>
        <div class="hero-sub">
            서울시 자치구별 생활쓰레기 · 음식물쓰레기 · 재활용품 배출 정보를
            앱처럼 한눈에 확인하세요.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# 검색 영역
# -----------------------------
st.markdown('<div class="search-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">자치구 선택</div>', unsafe_allow_html=True)

f1, f2 = st.columns([1.5, 0.5])

with f1:
    selected_gu = st.selectbox("자치구 선택", gu_list)

with f2:
    show_raw = st.checkbox("원본 데이터 보기", value=False)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 필터링
# -----------------------------
filtered = df[df[gu_col].astype(str).str.strip() == selected_gu].copy()

# -----------------------------
# 본문
# -----------------------------
st.subheader(f"📍 {selected_gu} 배출 정보")

if filtered.empty:
    st.warning("선택한 자치구 데이터가 없습니다.")
    st.stop()

row = filtered.iloc[0]

place_type = pretty_text(row[place_type_col]) if place_type_col else "정보 없음"
place = pretty_text(row[place_col]) if place_col else "정보 없음"

life_info = extract_info(row, "생활")
food_info = extract_info(row, "음식물")
recycle_info = extract_info(row, "재활용")

today_idx = datetime.now().weekday()
today_day = INDEX_TO_DAY[today_idx]

today_available = []
for item in [life_info, food_info, recycle_info]:
    flag = is_collectable_today(item["day_list"])
    if flag is True:
        today_available.append(f'{item["emoji"]} {item["title"]}')

st.markdown(
    f"""
    <div class="today-box">
        <div class="today-title">📅 오늘 요일: {today_day}</div>
        <div class="today-sub">선택한 자치구의 배출 가능 항목을 확인합니다.</div>
    </div>
    """,
    unsafe_allow_html=True
)

if today_available:
    st.success("오늘 배출 가능한 항목: " + ", ".join(today_available))
else:
    st.warning("오늘 배출 가능한 항목이 없거나 확인할 수 없습니다.")

c1, c2, c3 = st.columns(3)

with c1:
    render_native_card("생활쓰레기", "🛍️", life_info, place_type, place)

with c2:
    render_native_card("음식물", "🍎", food_info, place_type, place)

with c3:
    render_native_card("재활용품", "♻️", recycle_info, place_type, place)

# -----------------------------
# 하단 정보 카드
# -----------------------------
st.markdown('<div class="glass-wrap">', unsafe_allow_html=True)

g1, g2, g3, g4 = st.columns(4)

nocollect_val = pretty_text(row[nocollect_col]) if nocollect_col else "정보 없음"
dept_val = pretty_text(row[dept_col]) if dept_col else "정보 없음"
phone_val = pretty_text(row[phone_col]) if phone_col else "정보 없음"
base_date = pretty_text(row[date_col]) if date_col else "정보 없음"
updated_date = pretty_text(row[updated_col]) if updated_col else "정보 없음"

with g1:
    render_glass_info_card(
        "미수거일",
        nocollect_val,
        "공휴일 또는 자치구 사정에 따라 변동될 수 있어요"
    )

with g2:
    render_glass_info_card(
        "관리부서",
        dept_val,
        "자세한 배출 기준은 담당 부서 안내를 확인하세요"
    )

with g3:
    render_glass_info_card(
        "전화번호",
        phone_val,
        "문의가 필요할 때 바로 확인할 수 있어요"
    )

with g4:
    render_glass_info_card(
        "기준일 / 수정일",
        f"{base_date}<br>{updated_date}",
        "데이터 최신 여부를 함께 확인하세요"
    )

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 안내 문구
# -----------------------------
st.markdown(
    """
    <div class="footer-box">
        <div class="section-title">🔎 이용 안내</div>
        <div class="note-text">
            자치구마다 배출요일, 배출시간, 배출방법이 다를 수 있습니다.<br>
            실제 배출 전에는 담당 부서 또는 자치구 공식 안내를 함께 확인해주세요.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# 원본 데이터
# -----------------------------
if show_raw:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("원본 데이터")
    st.dataframe(filtered, use_container_width=True)
