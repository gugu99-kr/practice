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
.stApp {
    background:
        radial-gradient(circle at top left, rgba(99, 102, 241, 0.08), transparent 22%),
        radial-gradient(circle at top right, rgba(56, 189, 248, 0.10), transparent 24%),
        linear-gradient(180deg, #eef4ff 0%, #f8fbff 45%, #f5f7fb 100%);
}

.block-container {
    max-width: 1180px;
    padding-top: 1.4rem;
    padding-bottom: 2rem;
}

.hero-box {
    background: linear-gradient(135deg, #4f8cff 0%, #79b8ff 100%);
    padding: 28px 32px;
    border-radius: 28px;
    color: white;
    margin-bottom: 20px;
    box-shadow: 0 12px 30px rgba(79, 140, 255, 0.20);
}

.hero-title {
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 0.4rem;
}

.hero-sub {
    font-size: 1rem;
    opacity: 0.95;
    line-height: 1.6;
}

.search-box {
    background: rgba(255,255,255,0.76);
    border: 1px solid rgba(148,163,184,0.12);
    border-radius: 24px;
    padding: 18px;
    margin-bottom: 18px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
}

.card {
    background: rgba(255,255,255,0.88);
    border-radius: 26px;
    padding: 24px 20px;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
    border: 1px solid rgba(148, 163, 184, 0.12);
    min-height: 340px;
}

.card-title {
    font-size: 1.7rem;
    font-weight: 800;
    margin-bottom: 18px;
    color: #0f172a;
}

.label {
    font-size: 0.9rem;
    color: #64748b;
    margin-top: 14px;
    margin-bottom: 4px;
    font-weight: 700;
}

.value {
    font-size: 1.02rem;
    font-weight: 600;
    color: #111827;
    line-height: 1.65;
    word-break: keep-all;
    overflow-wrap: break-word;
    white-space: pre-wrap;
}

.small-box {
    background: rgba(255,255,255,0.86);
    border-radius: 18px;
    padding: 16px;
    border: 1px solid rgba(148,163,184,0.10);
    min-height: 110px;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
}

.footer-box {
    background: white;
    border-radius: 22px;
    padding: 20px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.05);
    border: 1px solid rgba(0,0,0,0.04);
    margin-top: 18px;
}

.note-text {
    color: #475467;
    font-size: 0.95rem;
    line-height: 1.7;
}

.section-title {
    font-size: 1.2rem;
    font-weight: 800;
    margin-bottom: 8px;
    color: #0f172a;
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


def normalize_time_piece(val):
    text = safe_text(val)
    if text == "정보 없음":
        return text

    text = str(text).strip()

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


def esc(val):
    return html.escape(str(val))


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
    day = normalize_day_text(row[day_col]) if day_col else "정보 없음"
    time_text = normalize_time_text(
        row[start_col] if start_col else None,
        row[end_col] if end_col else None
    )

    return {
        "method": method,
        "day": day,
        "time": time_text
    }


def render_card(title, emoji, info, place_type, place):
    title = esc(title)
    emoji = esc(emoji)
    day = esc(info.get("day", "정보 없음"))
    time_val = esc(info.get("time", "정보 없음"))
    method = esc(info.get("method", "정보 없음"))
    place_type = esc(place_type)
    place = esc(place)

    card_html = f"""
    <div class="card">
        <div class="card-title">{emoji} {title}</div>

        <div class="label">🗓️ 배출 요일</div>
        <div class="value">{day}</div>

        <div class="label">⏰ 배출 시간</div>
        <div class="value">{time_val}</div>

        <div class="label">📝 배출 방법</div>
        <div class="value">{method}</div>

        <div class="label">📍 배출 장소 유형</div>
        <div class="value">{place_type}</div>

        <div class="label">🏠 상세 장소</div>
        <div class="value">{place}</div>
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

# 주요 컬럼 찾기
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

# 서울 데이터만 남기기
if sido_col and sido_col in df.columns:
    df = df[df[sido_col].astype(str).str.contains("서울", na=False)].copy()

gu_list = sorted(df[gu_col].dropna().astype(str).str.strip().unique().tolist())

if not gu_list:
    st.error("구 목록을 불러오지 못했습니다. 데이터 내용을 확인해주세요.")
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
st.markdown('<div class="section-title">검색 조건</div>', unsafe_allow_html=True)

f1, f2, f3 = st.columns([1.2, 1.4, 0.8])

with f1:
    selected_gu = st.selectbox("자치구 선택", gu_list)

with f2:
    keyword = st.text_input(
        "배출장소/방법 키워드 검색",
        placeholder="예: 문전수거, 거점배출, 클린하우스"
    )

with f3:
    show_raw = st.checkbox("원본 데이터 보기", value=False)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 필터링
# -----------------------------
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

# -----------------------------
# 본문
# -----------------------------
st.subheader(f"📍 {selected_gu} 배출 정보")

if filtered.empty:
    st.warning("검색 조건에 맞는 데이터가 없습니다.")
    st.stop()

# 디버깅 필요하면 잠깐 True로 바꾸기
DEBUG_MODE = False

row = filtered.iloc[0]

place_type = pretty_text(row[place_type_col]) if place_type_col else "정보 없음"
place = pretty_text(row[place_col]) if place_col else "정보 없음"

life_info = extract_info(row, "생활")
food_info = extract_info(row, "음식물")
recycle_info = extract_info(row, "재활용")

if DEBUG_MODE:
    st.write("생활:", life_info)
    st.write("음식물:", food_info)
    st.write("재활용:", recycle_info)

c1, c2, c3 = st.columns(3)

with c1:
    render_card("생활쓰레기", "🛍️", life_info, place_type, place)

with c2:
    render_card("음식물", "🍎", food_info, place_type, place)

with c3:
    render_card("재활용품", "♻️", recycle_info, place_type, place)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------
# 추가 정보
# -----------------------------
a, b, c, d = st.columns(4)

with a:
    st.markdown(
        f"""
        <div class="small-box">
            <div class="label">미수거일</div>
            <div class="value">{esc(pretty_text(row[nocollect_col]) if nocollect_col else "정보 없음")}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with b:
    st.markdown(
        f"""
        <div class="small-box">
            <div class="label">관리부서</div>
            <div class="value">{esc(pretty_text(row[dept_col]) if dept_col else "정보 없음")}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c:
    st.markdown(
        f"""
        <div class="small-box">
            <div class="label">전화번호</div>
            <div class="value">{esc(pretty_text(row[phone_col]) if phone_col else "정보 없음")}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with d:
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
