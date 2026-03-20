import re
import html
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
        radial-gradient(circle at 15% 10%, rgba(96, 165, 250, 0.18), transparent 22%),
        radial-gradient(circle at 85% 12%, rgba(125, 211, 252, 0.16), transparent 20%),
        linear-gradient(180deg, #dfeeff 0%, #eef6ff 34%, #f6f9ff 100%);
}

.block-container {
    max-width: 1200px;
    padding-top: 1.2rem;
    padding-bottom: 2.2rem;
}

/* 기본 위젯 둥글게 */
div[data-testid="stSelectbox"] > div,
div[data-testid="stCheckbox"] {
    border-radius: 16px !important;
}

/* 상단 히어로 */
.hero-shell {
    background: rgba(255,255,255,0.22);
    border: 1px solid rgba(255,255,255,0.35);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 34px;
    padding: 12px;
    box-shadow: 0 18px 44px rgba(31, 41, 55, 0.10);
    margin-bottom: 18px;
}

.hero-box {
    background:
        linear-gradient(135deg, rgba(76, 132, 255, 0.96) 0%, rgba(112, 175, 255, 0.94) 58%, rgba(70, 135, 255, 0.92) 100%);
    border-radius: 28px;
    padding: 30px 28px;
    color: white;
    position: relative;
    overflow: hidden;
}

.hero-box::before {
    content: "";
    position: absolute;
    right: -40px;
    top: -40px;
    width: 180px;
    height: 180px;
    border-radius: 50%;
    background: rgba(255,255,255,0.12);
}

.hero-box::after {
    content: "";
    position: absolute;
    left: 42%;
    bottom: -55px;
    width: 140px;
    height: 140px;
    border-radius: 50%;
    background: rgba(255,255,255,0.08);
}

.hero-topline {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.20);
    border-radius: 999px;
    padding: 7px 12px;
    font-size: 0.82rem;
    font-weight: 700;
    margin-bottom: 12px;
    position: relative;
    z-index: 2;
}

.hero-title {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin-bottom: 0.45rem;
    position: relative;
    z-index: 2;
}

.hero-sub {
    font-size: 1rem;
    line-height: 1.65;
    opacity: 0.97;
    position: relative;
    z-index: 2;
}

/* 검색 박스 */
.search-box {
    background: rgba(255,255,255,0.58);
    border: 1px solid rgba(255,255,255,0.35);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 26px;
    padding: 18px;
    margin-bottom: 18px;
    box-shadow: 0 12px 28px rgba(31, 41, 55, 0.06);
}

.section-title {
    font-size: 1.08rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 8px;
}

.section-sub {
    font-size: 0.92rem;
    color: #64748b;
    margin-bottom: 2px;
}

/* 오늘 상태 */
.today-box {
    background: rgba(255,255,255,0.62);
    border: 1px solid rgba(255,255,255,0.40);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 24px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 12px 24px rgba(31, 41, 55, 0.05);
}

.today-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 4px;
}

.today-sub {
    font-size: 0.92rem;
    color: #64748b;
}

/* 메인 카드 */
.waste-card {
    background: linear-gradient(
        180deg,
        rgba(255,255,255,0.58) 0%,
        rgba(255,255,255,0.34) 100%
    );
    border: 1px solid rgba(255,255,255,0.42);
    border-radius: 30px;
    padding: 22px 20px 20px 20px;
    min-height: 540px;
    box-shadow:
        0 16px 34px rgba(15, 23, 42, 0.08),
        inset 0 1px 0 rgba(255,255,255,0.50);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    overflow: hidden;
}

.card-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
}

.card-icon {
    width: 52px;
    height: 52px;
    border-radius: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    background: rgba(255,255,255,0.55);
    border: 1px solid rgba(255,255,255,0.50);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.55);
    flex-shrink: 0;
}

.card-head-text {
    min-width: 0;
}

.waste-card-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.2;
    margin-bottom: 2px;
}

.waste-card-sub {
    font-size: 0.88rem;
    color: #64748b;
}

.status-badge {
    display: inline-block;
    margin-bottom: 14px;
    padding: 8px 13px;
    border-radius: 999px;
    font-size: 0.84rem;
    font-weight: 800;
    border: 1px solid transparent;
}

.status-ok {
    background: rgba(34, 197, 94, 0.12);
    color: #166534;
    border-color: rgba(34, 197, 94, 0.15);
}

.status-no {
    background: rgba(245, 158, 11, 0.14);
    color: #92400e;
    border-color: rgba(245, 158, 11, 0.18);
}

.status-unknown {
    background: rgba(148, 163, 184, 0.16);
    color: #475569;
    border-color: rgba(148, 163, 184, 0.15);
}

.info-group {
    background: rgba(255,255,255,0.34);
    border: 1px solid rgba(255,255,255,0.30);
    border-radius: 20px;
    padding: 14px 14px 12px 14px;
    margin-top: 10px;
}

.waste-label {
    font-size: 0.78rem;
    color: #64748b;
    font-weight: 800;
    letter-spacing: 0.01em;
    margin-bottom: 4px;
}

.waste-value {
    font-size: 0.98rem;
    color: #111827;
    font-weight: 700;
    line-height: 1.55;
    word-break: keep-all;
    overflow-wrap: break-word;
    white-space: pre-wrap;
}

/* 하단 글래스 카드 */
.glass-card {
    background: linear-gradient(
        180deg,
        rgba(255,255,255,0.52) 0%,
        rgba(255,255,255,0.26) 100%
    );
    border: 1px solid rgba(255,255,255,0.40);
    border-radius: 26px;
    padding: 18px;
    min-height: 132px;
    box-shadow:
        0 12px 28px rgba(15, 23, 42, 0.07),
        inset 0 1px 0 rgba(255,255,255,0.45);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    overflow: hidden;
}

.glass-label {
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: #64748b;
    font-weight: 800;
    margin-bottom: 10px;
}

.glass-value {
    font-size: 1rem;
    line-height: 1.45;
    color: #0f172a;
    font-weight: 700;
    word-break: keep-all;
    overflow-wrap: break-word;
}

.glass-sub {
    font-size: 0.85rem;
    color: #64748b;
    margin-top: 8px;
    line-height: 1.45;
}

/* 안내문 */
.footer-box {
    background: rgba(255,255,255,0.64);
    border-radius: 24px;
    padding: 20px;
    box-shadow: 0 10px 22px rgba(0,0,0,0.05);
    border: 1px solid rgba(255,255,255,0.40);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    margin-top: 18px;
}

.note-text {
    color: #475467;
    font-size: 0.95rem;
    line-height: 1.7;
}

@media (max-width: 900px) {
    .hero-title {
        font-size: 1.65rem;
    }
    .waste-card {
        min-height: auto;
    }
    .glass-card {
        min-height: 112px;
    }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

DAY_ORDER = ["월", "화", "수", "목", "금", "토", "일"]
DAY_TO_INDEX = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}
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


def esc(val):
    return html.escape(str(val))


def normalize_day_text(val):
    text = safe_text(val)
    if text == "정보 없음":
        return text

    raw = text.replace(" ", "")
    tokens = re.split(r"[+,/·ㆍ\s]+", raw)
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
    tokens = re.split(r"[+,/·ㆍ\s]+", raw)
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


def get_status_badge(flag):
    if flag is True:
        return '<div class="status-badge status-ok">오늘 배출 가능</div>'
    if flag is False:
        return '<div class="status-badge status-no">오늘 배출일 아님</div>'
    return '<div class="status-badge status-unknown">확인 불가</div>'


def render_card_html(title, emoji, info, place_type, place):
    today_flag = is_collectable_today(info["day_list"])
    badge_html = get_status_badge(today_flag)

    card_html = f"""
    <div class="waste-card">
        <div class="card-head">
            <div class="card-icon">{esc(emoji)}</div>
            <div class="card-head-text">
                <div class="waste-card-title">{esc(title)}</div>
                <div class="waste-card-sub">배출 규칙 안내</div>
            </div>
        </div>

        {badge_html}

        <div class="info-group">
            <div class="waste-label">🗓️ 배출 요일</div>
            <div class="waste-value">{esc(info["day"])}</div>
        </div>

        <div class="info-group">
            <div class="waste-label">⏰ 배출 시간</div>
            <div class="waste-value">{esc(info["time"])}</div>
        </div>

        <div class="info-group">
            <div class="waste-label">📝 배출 방법</div>
            <div class="waste-value">{esc(info["method"])}</div>
        </div>

        <div class="info-group">
            <div class="waste-label">📍 배출 장소 유형</div>
            <div class="waste-value">{esc(place_type)}</div>
        </div>

        <div class="info-group">
            <div class="waste-label">🏠 상세 장소</div>
            <div class="waste-value">{esc(place)}</div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_glass_info_card(label, value, sub_text=""):
    card_html = f"""
    <div class="glass-card">
        <div class="glass-label">{esc(label)}</div>
        <div class="glass-value">{value}</div>
        <div class="glass-sub">{esc(sub_text)}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


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
    <div class="hero-shell">
        <div class="hero-box">
            <div class="hero-topline">Seoul Waste Helper</div>
            <div class="hero-title">🗑️ 우리 구 쓰레기 배출 도우미</div>
            <div class="hero-sub">
                서울시 자치구별 생활쓰레기 · 음식물쓰레기 · 재활용품 배출 정보를
                아이폰 날씨앱 느낌의 카드 UI로 한눈에 확인하세요.
            </div>
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
st.markdown('<div class="section-sub">확인할 자치구를 선택하세요.</div>', unsafe_allow_html=True)

f1, f2 = st.columns([1.5, 0.5])

with f1:
    selected_gu = st.selectbox("자치구 선택", gu_list, label_visibility="collapsed")

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
    if is_collectable_today(item["day_list"]) is True:
        today_available.append(f'{item["emoji"]} {item["title"]}')

st.markdown(
    f"""
    <div class="today-box">
        <div class="today-title">📅 오늘 요일: {today_day}</div>
        <div class="today-sub">선택한 자치구 기준 오늘 배출 가능한 항목을 안내합니다.</div>
    </div>
    """,
    unsafe_allow_html=True
)

if today_available:
    st.success("오늘 배출 가능한 항목: " + ", ".join(today_available))
else:
    st.warning("오늘 배출 가능한 항목이 없거나 확인할 수 없습니다.")

c1, c2, c3 = st.columns(3, gap="large")

with c1:
    render_card_html("생활쓰레기", "🛍️", life_info, place_type, place)

with c2:
    render_card_html("음식물", "🍎", food_info, place_type, place)

with c3:
    render_card_html("재활용품", "♻️", recycle_info, place_type, place)

# -----------------------------
# 하단 정보 카드
# -----------------------------
st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

g1, g2, g3, g4 = st.columns(4, gap="large")

nocollect_val = pretty_text(row[nocollect_col]) if nocollect_col else "정보 없음"
dept_val = pretty_text(row[dept_col]) if dept_col else "정보 없음"
phone_val = pretty_text(row[phone_col]) if phone_col else "정보 없음"
base_date = pretty_text(row[date_col]) if date_col else "정보 없음"
updated_date = pretty_text(row[updated_col]) if updated_col else "정보 없음"

with g1:
    render_glass_info_card(
        "미수거일",
        esc(nocollect_val),
        "공휴일 또는 자치구 사정에 따라 달라질 수 있어요"
    )

with g2:
    render_glass_info_card(
        "관리부서",
        esc(dept_val),
        "세부 기준은 담당 부서 안내를 확인하세요"
    )

with g3:
    render_glass_info_card(
        "전화번호",
        esc(phone_val),
        "문의가 필요할 때 바로 확인할 수 있어요"
    )

with g4:
    render_glass_info_card(
        "기준일 / 수정일",
        f"{esc(base_date)}<br>{esc(updated_date)}",
        "데이터 최신 여부를 함께 확인하세요"
    )

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
