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
# 기본 스타일
# -----------------------------
st.markdown("""
<style>
.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.hero {
    background: linear-gradient(135deg, #4f8cff 0%, #87b7ff 100%);
    color: white;
    padding: 28px;
    border-radius: 24px;
    margin-bottom: 20px;
    box-shadow: 0 8px 24px rgba(79,140,255,0.18);
}
.hero h1 {
    margin: 0 0 6px 0;
    font-size: 2rem;
}
.hero p {
    margin: 0;
    opacity: 0.95;
}
.card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    min-height: 280px;
}
.card-title {
    font-size: 1.15rem;
    font-weight: 700;
    margin-bottom: 10px;
}
.label {
    color: #6b7280;
    font-size: 0.9rem;
    margin-top: 10px;
}
.value {
    color: #111827;
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.55;
    white-space: pre-wrap;
    word-break: keep-all;
    overflow-wrap: break-word;
}
.subbox {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 14px 16px;
}
</style>
""", unsafe_allow_html=True)

DAY_ORDER = ["월", "화", "수", "목", "금", "토", "일"]


# -----------------------------
# 유틸
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
    tokens = re.split(r"[+,/·ㆍ\s]+", raw)
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


def normalize_time_range(start, end):
    s = normalize_time_piece(start)
    e = normalize_time_piece(end)

    if s == "정보 없음" and e == "정보 없음":
        return "정보 없음"
    if s != "정보 없음" and e != "정보 없음":
        return f"{s} ~ {e}"
    return s if s != "정보 없음" else e


def find_column(df, candidates):
    cols = {str(c).strip(): c for c in df.columns}
    for cand in candidates:
        if cand in cols:
            return cols[cand]
    return None


def esc(val):
    return html.escape(pretty_text(val))


@st.cache_data
def load_data(path):
    last_error = None
    for enc in ["cp949", "utf-8-sig", "utf-8", "euc-kr"]:
        try:
            df = pd.read_csv(path, encoding=enc)
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception as e:
            last_error = e
    raise ValueError(f"CSV를 읽지 못했습니다: {last_error}")


def extract_info(row, prefix):
    day_col = f"{prefix}배출요일"
    start_col = f"{prefix}배출시작시각"
    end_col = f"{prefix}배출종료시각"
    method_col = f"{prefix}배출방법"

    return {
        "day": normalize_day_text(row[day_col]) if day_col in row.index else "정보 없음",
        "time": normalize_time_range(
            row[start_col] if start_col in row.index else None,
            row[end_col] if end_col in row.index else None,
        ),
        "method": pretty_text(row[method_col]) if method_col in row.index else "정보 없음",
    }


def render_card(title, emoji, info, place_type, place):
    st.markdown(f"""
    <div class="card">
        <div class="card-title">{emoji} {html.escape(title)}</div>

        <div class="label">배출요일</div>
        <div class="value">{html.escape(info["day"])}</div>

        <div class="label">배출시간</div>
        <div class="value">{html.escape(info["time"])}</div>

        <div class="label">배출방법</div>
        <div class="value">{html.escape(info["method"])}</div>

        <div class="label">배출장소 유형</div>
        <div class="value">{html.escape(place_type)}</div>

        <div class="label">배출장소</div>
        <div class="value">{html.escape(place)}</div>
    </div>
    """, unsafe_allow_html=True)


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

# 주요 컬럼
sido_col = find_column(df, ["시도명"])
gu_col = find_column(df, ["시군구명", "자치구명", "구명"])
zone_col = find_column(df, ["관리구역명"])
target_col = find_column(df, ["관리구역대상지역명"])
place_type_col = find_column(df, ["배출장소유형"])
place_col = find_column(df, ["배출장소"])
nocollect_col = find_column(df, ["미수거일"])
dept_col = find_column(df, ["관리부서명"])
phone_col = find_column(df, ["관리부서전화번호"])
date_col = find_column(df, ["데이터기준일자"])
updated_col = find_column(df, ["최종수정시점"])

if gu_col is None:
    st.error("`시군구명` 컬럼을 찾지 못했습니다.")
    st.write("현재 컬럼:", list(df.columns))
    st.stop()

# 서울만 필터
if sido_col:
    df = df[df[sido_col].astype(str).str.contains("서울", na=False)].copy()

# 구 목록
gu_list = sorted(df[gu_col].dropna().astype(str).str.strip().unique().tolist())

if not gu_list:
    st.error("자치구 목록을 만들 수 없습니다.")
    st.stop()

# -----------------------------
# 헤더
# -----------------------------
st.markdown("""
<div class="hero">
    <h1>🗑️ 우리 구 쓰레기 배출 도우미</h1>
    <p>서울시 자치구별 생활쓰레기 · 음식물쓰레기 · 재활용품 배출 규칙을 빠르게 확인하세요.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:
    st.header("검색")
    selected_gu = st.selectbox("자치구", gu_list)

    gu_df = df[df[gu_col].astype(str).str.strip() == selected_gu].copy()

    # 같은 구에 여러 행이 있으면 관리구역 선택
    if len(gu_df) > 1:
        if zone_col and target_col:
            gu_df["선택라벨"] = gu_df.apply(
                lambda r: f"{safe_text(r[zone_col])} | {safe_text(r[target_col])}",
                axis=1
            )
        elif target_col:
            gu_df["선택라벨"] = gu_df[target_col].apply(safe_text)
        elif zone_col:
            gu_df["선택라벨"] = gu_df[zone_col].apply(safe_text)
        else:
            gu_df["선택라벨"] = [f"{i+1}번 구역" for i in range(len(gu_df))]

        selected_label = st.selectbox("관리구역/대상지역", gu_df["선택라벨"].tolist())
        selected_row = gu_df[gu_df["선택라벨"] == selected_label].iloc[0]
    else:
        selected_row = gu_df.iloc[0]

    show_raw = st.checkbox("선택 구 전체 데이터 보기", value=False)

# -----------------------------
# 본문
# -----------------------------
st.subheader(f"📍 {selected_gu} 배출 정보")

if zone_col and safe_text(selected_row[zone_col]) != "정보 없음":
    st.caption(f"관리구역: {safe_text(selected_row[zone_col])}")

if target_col and safe_text(selected_row[target_col]) != "정보 없음":
    st.caption(f"대상지역: {safe_text(selected_row[target_col])}")

place_type = pretty_text(selected_row[place_type_col]) if place_type_col else "정보 없음"
place = pretty_text(selected_row[place_col]) if place_col else "정보 없음"

life_info = extract_info(selected_row, "생활쓰레기")
food_info = extract_info(selected_row, "음식물쓰레기")
recycle_info = extract_info(selected_row, "재활용품")

c1, c2, c3 = st.columns(3)

with c1:
    render_card("생활쓰레기", "🛍️", life_info, place_type, place)
with c2:
    render_card("음식물쓰레기", "🍎", food_info, place_type, place)
with c3:
    render_card("재활용품", "♻️", recycle_info, place_type, place)

st.markdown("<br>", unsafe_allow_html=True)

a, b, c, d = st.columns(4)

with a:
    st.markdown(f"""
    <div class="subbox">
        <div class="label">미수거일</div>
        <div class="value">{html.escape(pretty_text(selected_row[nocollect_col]) if nocollect_col else "정보 없음")}</div>
    </div>
    """, unsafe_allow_html=True)

with b:
    st.markdown(f"""
    <div class="subbox">
        <div class="label">관리부서</div>
        <div class="value">{html.escape(pretty_text(selected_row[dept_col]) if dept_col else "정보 없음")}</div>
    </div>
    """, unsafe_allow_html=True)

with c:
    st.markdown(f"""
    <div class="subbox">
        <div class="label">전화번호</div>
        <div class="value">{html.escape(pretty_text(selected_row[phone_col]) if phone_col else "정보 없음")}</div>
    </div>
    """, unsafe_allow_html=True)

with d:
    base_date = pretty_text(selected_row[date_col]) if date_col else "정보 없음"
    updated_date = pretty_text(selected_row[updated_col]) if updated_col else "정보 없음"
    st.markdown(f"""
    <div class="subbox">
        <div class="label">기준일 / 수정일</div>
        <div class="value">{html.escape(base_date)}<br>{html.escape(updated_date)}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.info("같은 자치구 안에서도 관리구역에 따라 배출요일이 다를 수 있습니다. 왼쪽에서 관리구역/대상지역까지 선택해서 확인하세요.")

# -----------------------------
# 전체 구 데이터 보기
# -----------------------------
if show_raw:
    st.subheader("선택 자치구 전체 데이터")

    preview_cols = [col for col in [
        gu_col, zone_col, target_col, place_type_col, place_col,
        "생활쓰레기배출요일", "생활쓰레기배출시작시각", "생활쓰레기배출종료시각", "생활쓰레기배출방법",
        "음식물쓰레기배출요일", "음식물쓰레기배출시작시각", "음식물쓰레기배출종료시각", "음식물쓰레기배출방법",
        "재활용품배출요일", "재활용품배출시작시각", "재활용품배출종료시각", "재활용품배출방법",
        nocollect_col, dept_col, phone_col
    ] if col is not None and col in gu_df.columns]

    preview_df = gu_df[preview_cols].copy()

    for col in preview_df.columns:
        if "요일" in col:
            preview_df[col] = preview_df[col].apply(normalize_day_text)
        else:
            preview_df[col] = preview_df[col].apply(pretty_text)

    st.dataframe(preview_df, use_container_width=True)
