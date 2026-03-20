import re
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
.main {
    background: linear-gradient(180deg, #f7fbff 0%, #eef6ff 100%);
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}
.hero-box {
    background: linear-gradient(135deg, #4f8cff 0%, #79b8ff 100%);
    padding: 28px 32px;
    border-radius: 24px;
    color: white;
    box-shadow: 0 8px 24px rgba(79, 140, 255, 0.18);
    margin-bottom: 20px;
}
.hero-title {
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 0.4rem;
}
.hero-sub {
    font-size: 1rem;
    opacity: 0.95;
}
.card {
    background: white;
    border-radius: 22px;
    padding: 22px 20px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.04);
    min-height: 320px;
}
.card-title {
    font-size: 1.25rem;
    font-weight: 800;
    margin-bottom: 12px;
}
.label {
    font-size: 0.88rem;
    color: #667085;
    margin-top: 12px;
    margin-bottom: 2px;
}
.value {
    font-size: 1rem;
    font-weight: 600;
    color: #111827;
    line-height: 1.6;
    word-break: keep-all;
    overflow-wrap: break-word;
}
.small-box {
    background: rgba(255,255,255,0.75);
    border-radius: 18px;
    padding: 14px 16px;
    border: 1px solid rgba(0,0,0,0.04);
    min-height: 110px;
}
.footer-box {
    background: white;
    border-radius: 20px;
    padding: 18px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.05);
    border: 1px solid rgba(0,0,0,0.04);
}
.note-text {
    color: #475467;
    font-size: 0.95rem;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

DAY_ORDER = ["월", "화", "수", "목", "금", "토", "일"]


# -----------------------------
# 유틸 함수
# -----------------------------
def safe_text(val):
    """NaN/공백 대응"""
    if pd.isna(val):
        return "정보 없음"
    text = str(val).strip()
    return text if text else "정보 없음"


def pretty_text(text):
    """출력용 텍스트 정리"""
    text = safe_text(text)
    if text == "정보 없음":
        return text

    # 띄어쓰기 및 기호 정리
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace(" ,", ",")
    text = text.replace(" + ", " · ")
    text = text.replace("+", " · ")
    text = text.replace("건물앞", "건물 앞")
    text = text.replace("점포앞", "점포 앞")
    text = text.replace("대문앞", "대문 앞")

    return text


def find_column(df, candidates):
    """후보 컬럼명 중 실제 존재하는 컬럼 반환"""
    normalized = {str(col).strip(): col for col in df.columns}
    for cand in candidates:
        if cand in normalized:
            return normalized[cand]
    return None


def normalize_day_text(text):
    """요일 문자열 정리: 중복 제거 + 월~일 순서 정렬"""
    if pd.isna(text):
        return "정보 없음"

    s = str(text).strip()
    if not s:
        return "정보 없음"

    # 불필요 공백 제거
    s = s.replace(" ", "")

    # 구분자 기준 분리
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
    """시간 한 조각 정리"""
    text = safe_text(value)
    if text == "정보 없음":
        return text

    text = str(text).strip()

    # 1800, 0900 형태 대응
    if re.fullmatch(r"\d{4}", text):
        return f"{text[:2]}:{text[2:]}"
    # 18 형태 대응
    if re.fullmatch(r"\d{1,2}", text):
        return f"{int(text):02d}:00"

    return text


def normalize_time_text(start, end):
    """시간 문자열 정리"""
    start = normalize_time_piece(start)
    end = normalize_time_piece(end)

    if start == "정보 없음" and end == "정보 없음":
        return "정보 없음"
    if start != "정보 없음" and end != "정보 없음":
        return f"{start} ~ {end}"
    return start if start != "정보 없음" else end


def merge_unique_values(series):
    """여러 행의 값을 중복 제거 후 합치기"""
    values = []
    for v in series.dropna():
        t = str(v).strip()
        if t and t not in values:
            values.append(t)

    if not values:
        return "정보 없음"

    return " / ".join(values)


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """
    CSV 로드:
    - cp949 / utf-8-sig / utf-8 순서로 시도
    - 컬럼명 공백 제거
    """
    encodings = ["cp949", "utf-8-sig", "utf-8"]

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
    """
    종류별 정보 추출
    kind: 생활 / 음식물 / 재활용
    """
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


def render_card(title, emoji, info, place_type, place):
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">{emoji} {title}</div>

            <div class="label">배출요일</div>
            <div class="value">{info["day"]}</div>

            <div class="label">배출시간</div>
            <div class="value">{info["time"]}</div>

            <div class="label">배출방법</div>
            <div class="value">{info["method"]}</div>

            <div class="label">배출장소 유형</div>
            <div class="value">{place_type}</div>

            <div class="label">배출장소</div>
            <div class="value">{place}</div>
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

# 문자열 정리
for col in df.columns:
    if df[col].dtype == "object":
        df[col] = df[col].astype(str).str.strip()

# 구 리스트
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
            서울시 자치구별 생활쓰레기 · 음식물쓰레기 · 재활용품 배출 요일과 방법을 한눈에 확인하세요.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# 사이드바 / 필터
# -----------------------------
with st.sidebar:
    st.header("검색 조건")
    selected_gu = st.selectbox("자치구 선택", gu_list)

    keyword = st.text_input(
        "배출장소/방법 키워드 검색",
        placeholder="예: 문전수거, 거점배출, 클린하우스"
    )

    show_raw = st.checkbox("원본 데이터 보기", value=False)

# 선택 구 필터
filtered = df[df[gu_col].astype(str).str.strip() == selected_gu].copy()

# 키워드 필터
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

# 첫 행 대표값 사용
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

st.markdown("<br>", unsafe_allow_html=True)

# 추가 정보
col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    st.markdown(
        f"""
        <div class="small-box">
            <div class="label">미수거일</div>
            <div class="value">{pretty_text(row[nocollect_col]) if nocollect_col else "정보 없음"}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_b:
    st.markdown(
        f"""
        <div class="small-box">
            <div class="label">관리부서</div>
            <div class="value">{pretty_text(row[dept_col]) if dept_col else "정보 없음"}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_c:
    st.markdown(
        f"""
        <div class="small-box">
            <div class="label">전화번호</div>
            <div class="value">{pretty_text(row[phone_col]) if phone_col else "정보 없음"}</div>
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
            <div class="value">{base_date}<br>{updated_date}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# 같은 구에 데이터가 여러 행일 때 참고 정보
if len(filtered) > 1:
    st.subheader("📋 같은 자치구의 추가 배출 정보")

    preview_cols = [gu_col]
    for c in [
        place_type_col,
        place_col,
        "생활쓰레기배출요일",
        "음식물쓰레기배출요일",
        "재활용품배출요일",
        "생활쓰레기배출방법",
        "음식물쓰레기배출방법",
        "재활용품배출방법",
    ]:
        if c is not None and c in filtered.columns and c not in preview_cols:
            preview_cols.append(c)

    preview_df = filtered[preview_cols].copy()

    rename_map = {
        gu_col: "자치구",
        place_type_col: "배출장소유형" if place_type_col else "",
        place_col: "배출장소" if place_col else "",
        "생활쓰레기배출요일": "생활요일",
        "음식물쓰레기배출요일": "음식물요일",
        "재활용품배출요일": "재활용요일",
        "생활쓰레기배출방법": "생활방법",
        "음식물쓰레기배출방법": "음식물방법",
        "재활용품배출방법": "재활용방법",
    }

    preview_df = preview_df.rename(columns=rename_map)

    for col in preview_df.columns:
        preview_df[col] = preview_df[col].apply(pretty_text)

    st.dataframe(preview_df, use_container_width=True)

st.markdown(
    """
    <div class="footer-box">
        <div class="card-title">🔎 이용 안내</div>
        <div class="note-text">
            자치구마다 배출요일, 배출시간, 배출방법이 다를 수 있습니다.<br>
            실제 배출 전에는 담당 부서 또는 자치구 공식 안내를 함께 확인해주세요.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 원본 데이터
if show_raw:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("원본 데이터")
    st.dataframe(filtered, use_container_width=True)
