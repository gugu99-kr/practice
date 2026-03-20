import json
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium


# =========================
# 기본 설정
# =========================
st.set_page_config(
    page_title="서울시 생활쓰레기 배출 정보 지도",
    page_icon="🗺️",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1.2rem;
}
.kpi-card {
    background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%);
    border: 1px solid #e9eef5;
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.04);
}
.kpi-title {
    font-size: 0.9rem;
    color: #6b7280;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #111827;
}
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    margin-top: 0.3rem;
    margin-bottom: 0.6rem;
}
.small-help {
    color: #6b7280;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

st.title("🗺️ 서울시 생활쓰레기 배출 정보 지도")
st.caption("구별 평균 배출량을 색으로 보고, 개별 배출장소 정보를 지도에서 확인할 수 있습니다.")


# =========================
# 파일 경로
# =========================
DATA_PATH = Path("cleaned_seoul_waste.csv")
GEOJSON_PATH = Path("seoul_gu.geojson")


# =========================
# 유틸 함수
# =========================
def find_first_matching_column(df, keywords, exclude_keywords=None):
    exclude_keywords = exclude_keywords or []
    for col in df.columns:
        col_str = str(col).strip()
        if all(k.lower() in col_str.lower() for k in keywords):
            if not any(ex.lower() in col_str.lower() for ex in exclude_keywords):
                return col
    return None


def detect_columns(df):
    lat_col = None
    lon_col = None
    location_col = None
    method_col = None
    recycling_col = None
    day_col = None
    contact_col = None
    volume_col = None
    gu_col = None

    if "lat" in df.columns:
        lat_col = "lat"
    if "lon" in df.columns:
        lon_col = "lon"
    if "location" in df.columns:
        location_col = "location"
    if "method" in df.columns:
        method_col = "method"
    if "recycling" in df.columns:
        recycling_col = "recycling"
    if "day" in df.columns:
        day_col = "day"
    if "contact" in df.columns:
        contact_col = "contact"
    if "volume" in df.columns:
        volume_col = "volume"
    if "gu" in df.columns:
        gu_col = "gu"

    if lat_col is None:
        lat_col = find_first_matching_column(df, ["위도"]) or find_first_matching_column(df, ["lat"])
    if lon_col is None:
        lon_col = find_first_matching_column(df, ["경도"]) or find_first_matching_column(df, ["lon"])
    if location_col is None:
        location_col = (
            find_first_matching_column(df, ["배출", "장소"])
            or find_first_matching_column(df, ["장소"])
            or find_first_matching_column(df, ["location"])
            or find_first_matching_column(df, ["주소"])
        )
    if method_col is None:
        method_col = (
            find_first_matching_column(df, ["배출", "방법"], exclude_keywords=["재활용"])
            or find_first_matching_column(df, ["method"], exclude_keywords=["recycling"])
        )
    if recycling_col is None:
        recycling_col = (
            find_first_matching_column(df, ["재활용"])
            or find_first_matching_column(df, ["recycling"])
        )
    if day_col is None:
        day_col = (
            find_first_matching_column(df, ["배출", "요일"])
            or find_first_matching_column(df, ["요일"])
            or find_first_matching_column(df, ["day"])
        )
    if contact_col is None:
        contact_col = (
            find_first_matching_column(df, ["연락처"])
            or find_first_matching_column(df, ["담당자"])
            or find_first_matching_column(df, ["contact"])
            or find_first_matching_column(df, ["전화"])
        )
    if volume_col is None:
        volume_col = (
            find_first_matching_column(df, ["배출량"])
            or find_first_matching_column(df, ["발생량"])
            or find_first_matching_column(df, ["volume"])
            or find_first_matching_column(df, ["수거량"])
        )
    if gu_col is None:
        gu_col = find_first_matching_column(df, ["gu"]) or find_first_matching_column(df, ["구"])

    return {
        "lat": lat_col,
        "lon": lon_col,
        "location": location_col,
        "method": method_col,
        "recycling": recycling_col,
        "day": day_col,
        "contact": contact_col,
        "volume": volume_col,
        "gu": gu_col,
    }


def extract_gu(text):
    if pd.isna(text):
        return "기타"
    text = str(text).strip()
    tokens = text.replace(",", " ").split()
    for token in tokens:
        if token.endswith("구") and len(token) >= 2:
            return token
    return "기타"


def load_geojson_property_name(geojson_path, candidate_props):
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])
    if not features:
        return None

    props = features[0].get("properties", {})
    prop_keys = list(props.keys())

    for key in candidate_props:
        if key in prop_keys:
            return key

    for key in prop_keys:
        lower = key.lower()
        if "name" in lower or "gu" in lower or "kor" in lower:
            return key

    return None


# =========================
# 데이터 로드
# =========================
@st.cache_data
def load_data(path):
    if not path.exists():
        return None
    return pd.read_csv(path)


df = load_data(DATA_PATH)

if df is None:
    st.error("`cleaned_seoul_waste.csv` 파일을 찾을 수 없습니다. app.py와 같은 폴더에 두세요.")
    st.stop()

if not GEOJSON_PATH.exists():
    st.error("`seoul_gu.geojson` 파일을 찾을 수 없습니다. app.py와 같은 폴더에 두세요.")
    st.stop()

df.columns = [str(c).strip() for c in df.columns]
cols = detect_columns(df)

required_minimum = ["location", "volume"]
missing_core = [k for k in required_minimum if cols[k] is None]
if missing_core:
    st.error(
        "필수 컬럼을 찾지 못했습니다. 최소한 `location(배출장소)`과 `volume(배출량)` 컬럼이 필요합니다.\n\n"
        f"현재 감지 결과: {cols}"
    )
    st.stop()

work_df = df.copy()

if cols["lat"] is not None:
    work_df["lat_std"] = pd.to_numeric(work_df[cols["lat"]], errors="coerce")
else:
    work_df["lat_std"] = pd.NA

if cols["lon"] is not None:
    work_df["lon_std"] = pd.to_numeric(work_df[cols["lon"]], errors="coerce")
else:
    work_df["lon_std"] = pd.NA

work_df["location_std"] = work_df[cols["location"]].astype(str).fillna("정보없음")
work_df["volume_std"] = pd.to_numeric(work_df[cols["volume"]], errors="coerce")

if cols["method"] is not None:
    work_df["method_std"] = work_df[cols["method"]].astype(str).fillna("정보없음")
else:
    work_df["method_std"] = "정보없음"

if cols["recycling"] is not None:
    work_df["recycling_std"] = work_df[cols["recycling"]].astype(str).fillna("정보없음")
else:
    work_df["recycling_std"] = "정보없음"

if cols["day"] is not None:
    work_df["day_std"] = work_df[cols["day"]].astype(str).fillna("정보없음")
else:
    work_df["day_std"] = "정보없음"

if cols["contact"] is not None:
    work_df["contact_std"] = work_df[cols["contact"]].astype(str).fillna("정보없음")
else:
    work_df["contact_std"] = "정보없음"

if cols["gu"] is not None:
    work_df["gu_std"] = work_df[cols["gu"]].astype(str).fillna("기타")
else:
    work_df["gu_std"] = work_df["location_std"].apply(extract_gu)

work_df = work_df.dropna(subset=["volume_std"])
work_df = work_df[work_df["gu_std"].notna()]
work_df["gu_std"] = work_df["gu_std"].astype(str).str.strip()
work_df = work_df[work_df["gu_std"] != "기타"]

# =========================
# 필터
# =========================
st.sidebar.header("🔎 필터")

gu_options = sorted(work_df["gu_std"].dropna().unique().tolist())
selected_gu = st.sidebar.selectbox("구 선택", ["전체"] + gu_options)

day_options = sorted([d for d in work_df["day_std"].dropna().unique().tolist() if str(d).strip() != ""])
selected_days = st.sidebar.multiselect("배출요일 선택", day_options)

method_options = sorted([m for m in work_df["method_std"].dropna().unique().tolist() if str(m).strip() != ""])
selected_methods = st.sidebar.multiselect("배출방법 선택", method_options)

show_markers = st.sidebar.checkbox("개별 배출장소 마커 표시", value=True)

filtered_df = work_df.copy()

if selected_gu != "전체":
    filtered_df = filtered_df[filtered_df["gu_std"] == selected_gu]

if selected_days:
    filtered_df = filtered_df[filtered_df["day_std"].isin(selected_days)]

if selected_methods:
    filtered_df = filtered_df[filtered_df["method_std"].isin(selected_methods)]

gu_df = (
    filtered_df.groupby("gu_std", as_index=False)["volume_std"]
    .mean()
    .rename(columns={"gu_std": "gu", "volume_std": "avg_volume"})
)

# =========================
# KPI
# =========================
total_rows = len(filtered_df)
total_gu = filtered_df["gu_std"].nunique() if not filtered_df.empty else 0
avg_volume = filtered_df["volume_std"].mean() if not filtered_df.empty else 0
marker_count = filtered_df[["lat_std", "lon_std"]].dropna().shape[0] if not filtered_df.empty else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">총 데이터 수</div>
        <div class="kpi-value">{total_rows:,}</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">표시 구 개수</div>
        <div class="kpi-value">{total_gu}</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">평균 배출량</div>
        <div class="kpi-value">{avg_volume:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">좌표 보유 장소 수</div>
        <div class="kpi-value">{marker_count:,}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# =========================
# GeoJSON 속성명
# =========================
candidate_props = [
    "SIG_KOR_NM", "SIGUNGU_NM", "name", "adm_nm", "gu_name", "GU_NM", "sggnm"
]
geo_prop = load_geojson_property_name(GEOJSON_PATH, candidate_props)

if geo_prop is None:
    st.error("GeoJSON에서 구 이름 속성을 찾지 못했습니다.")
    st.stop()

# =========================
# 지도
# =========================
st.markdown('<div class="section-title">지도</div>', unsafe_allow_html=True)

default_center = [37.5665, 126.9780]
zoom_start = 11

if selected_gu != "전체":
    points_for_center = filtered_df.dropna(subset=["lat_std", "lon_std"])
    if not points_for_center.empty:
        default_center = [
            float(points_for_center["lat_std"].mean()),
            float(points_for_center["lon_std"].mean())
        ]
        zoom_start = 12

m = folium.Map(
    location=default_center,
    zoom_start=zoom_start,
    tiles="CartoDB positron",
    control_scale=True
)

if not gu_df.empty:
    folium.Choropleth(
        geo_data=str(GEOJSON_PATH),
        data=gu_df,
        columns=["gu", "avg_volume"],
        key_on=f"feature.properties.{geo_prop}",
        fill_color="YlOrRd",
        fill_opacity=0.75,
        line_opacity=0.35,
        legend_name="구별 평균 쓰레기 배출량"
    ).add_to(m)

folium.GeoJson(
    str(GEOJSON_PATH),
    name="서울시 구 경계",
    style_function=lambda feature: {
        "fillColor": "transparent",
        "color": "#4b5563",
        "weight": 1.2,
        "fillOpacity": 0.0
    },
    highlight_function=lambda feature: {
        "fillColor": "#00000000",
        "color": "#111827",
        "weight": 2.2,
        "fillOpacity": 0.0
    },
    tooltip=folium.GeoJsonTooltip(
        fields=[geo_prop],
        aliases=["구 이름"],
        localize=True,
        sticky=False,
        labels=True
    )
).add_to(m)

if show_markers:
    marker_df = filtered_df.dropna(subset=["lat_std", "lon_std"]).copy()

    for _, row in marker_df.iterrows():
        popup_html = f"""
        <div style="width:260px; font-size:13px; line-height:1.6;">
            <div style="font-size:15px; font-weight:700; margin-bottom:8px;">배출장소 정보</div>
            <b>배출장소:</b> {row.get('location_std', '정보없음')}<br>
            <b>배출방법:</b> {row.get('method_std', '정보없음')}<br>
            <b>재활용 배출방법:</b> {row.get('recycling_std', '정보없음')}<br>
            <b>쓰레기 배출요일:</b> {row.get('day_std', '정보없음')}<br>
            <b>담당자 연락처:</b> {row.get('contact_std', '정보없음')}<br>
            <b>배출량:</b> {row.get('volume_std', '정보없음')}
        </div>
        """

        tooltip_text = str(row.get("location_std", "배출장소"))

        folium.CircleMarker(
            location=[float(row["lat_std"]), float(row["lon_std"])],
            radius=5,
            color="#2563eb",
            fill=True,
            fill_color="#3b82f6",
            fill_opacity=0.78,
            weight=1,
            tooltip=tooltip_text,
            popup=folium.Popup(popup_html, max_width=320)
        ).add_to(m)

st_folium(m, width=None, height=720)

# =========================
# 하단 표
# =========================
left, right = st.columns([1.1, 1])

with left:
    st.markdown('<div class="section-title">구별 평균 배출량</div>', unsafe_allow_html=True)
    if gu_df.empty:
        st.info("표시할 구별 집계 데이터가 없습니다.")
    else:
        st.dataframe(
            gu_df.sort_values("avg_volume", ascending=False).reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )

with right:
    st.markdown('<div class="section-title">선택된 데이터 미리보기</div>', unsafe_allow_html=True)
    preview_cols = [
        "gu_std", "location_std", "method_std", "recycling_std",
        "day_std", "contact_std", "volume_std"
    ]

    if filtered_df.empty:
        st.info("조건에 맞는 데이터가 없습니다.")
    else:
        preview_df = (
            filtered_df[preview_cols]
            .rename(columns={
                "gu_std": "구",
                "location_std": "배출장소",
                "method_std": "배출방법",
                "recycling_std": "재활용 배출방법",
                "day_std": "배출요일",
                "contact_std": "담당자 연락처",
                "volume_std": "배출량"
            })
            .head(100)
        )
        st.dataframe(preview_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown(
    f"""
    <div class="small-help">
    현재 사용 중인 파일:
    <br>- 데이터 파일: <code>{DATA_PATH.name}</code>
    <br>- 지도 경계 파일: <code>{GEOJSON_PATH.name}</code>
    <br>- GeoJSON 매칭 속성: <code>{geo_prop}</code>
    </div>
    """,
    unsafe_allow_html=True
)
