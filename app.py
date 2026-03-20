import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import time

st.set_page_config(layout="wide")
st.title("🗺️ 서울시 생활쓰레기 배출 지도")

# -----------------------------
# 🔑 카카오 API KEY
# -----------------------------
KAKAO_API_KEY = "여기에_본인_API_KEY_입력"

# -----------------------------
# 📍 주소 → 좌표 변환 함수
# -----------------------------
def get_lat_lon(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}

    try:
        response = requests.get(url, headers=headers, params=params)
        result = response.json()

        if result['documents']:
            x = result['documents'][0]['x']  # 경도
            y = result['documents'][0]['y']  # 위도
            return float(y), float(x)
        else:
            return None, None
    except:
        return None, None


# -----------------------------
# 📂 파일 업로드
# -----------------------------
st.sidebar.header("📂 데이터 업로드")

uploaded_csv = st.sidebar.file_uploader("CSV 업로드", type=["csv"])
uploaded_excel = st.sidebar.file_uploader("엑셀 업로드", type=["xlsx"])

if uploaded_csv is None or uploaded_excel is None:
    st.warning("👉 CSV + 엑셀 파일을 모두 업로드하세요")
    st.stop()

# -----------------------------
# 📊 데이터 로드
# -----------------------------
@st.cache_data
def load_main_data(file):
    df = pd.read_csv(file, encoding="cp949")
    return df

@st.cache_data
def load_stat_data(file):
    df_stat = pd.read_excel(file)
    return df_stat

df = load_main_data(uploaded_csv)
df_stat = load_stat_data(uploaded_excel)

# -----------------------------
# 🔍 컬럼 자동 대응 (유연 처리)
# -----------------------------
# CSV 컬럼명 맞추기
if "시도명" in df.columns:
    df = df[df["시도명"].str.contains("서울", na=False)]

# 엑셀 컬럼 맞추기 (필요시 수정)
df_stat = df_stat.rename(columns={
    "시군구": "시군구명",
    "합계": "배출량"
})

# 필요한 컬럼만 유지
if "배출량" in df_stat.columns:
    df_stat["배출량"] = pd.to_numeric(df_stat["배출량"], errors="coerce")
    df_stat = df_stat[["시군구명", "배출량"]]

# -----------------------------
# 🔗 데이터 merge
# -----------------------------
if "시군구명" in df.columns and "시군구명" in df_stat.columns:
    df = df.merge(df_stat, on="시군구명", how="left")
else:
    st.error("❌ '시군구명' 컬럼 확인 필요")
    st.stop()

# -----------------------------
# 📍 좌표 생성 (없을 때만)
# -----------------------------
if "위도" not in df.columns or "경도" not in df.columns:

    st.warning("⏳ 좌표 생성 중... (시간 소요)")

    lat_list = []
    lon_list = []

    address_col = "배출장소"  # 필요시 수정

    for addr in df[address_col]:
        if pd.isna(addr):
            lat_list.append(None)
            lon_list.append(None)
            continue

        lat, lon = get_lat_lon(addr)
        lat_list.append(lat)
        lon_list.append(lon)

        time.sleep(0.2)

    df["위도"] = lat_list
    df["경도"] = lon_list

    st.success("✅ 좌표 생성 완료")


# -----------------------------
# 🎛️ 필터
# -----------------------------
st.sidebar.header("📌 필터")

if "시군구명" in df.columns:
    gu_list = df["시군구명"].dropna().unique()
    selected_gu = st.sidebar.selectbox("자치구 선택", ["전체"] + list(gu_list))

    if selected_gu != "전체":
        df = df[df["시군구명"] == selected_gu]


# -----------------------------
# 🎨 색상 함수
# -----------------------------
def get_color(volume):
    if pd.isna(volume):
        return "gray"
    elif volume > 1000:
        return "red"
    elif volume > 500:
        return "orange"
    else:
        return "green"


# -----------------------------
# 🗺️ 지도 생성
# -----------------------------
m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)


# -----------------------------
# 📍 마커 추가
# -----------------------------
for _, row in df.iterrows():

    if pd.isna(row.get("위도")) or pd.isna(row.get("경도")):
        continue

    popup_html = f"""
    <b>📍 배출장소:</b> {row.get('배출장소', '')}<br>
    <b>🗑️ 배출방법:</b> {row.get('생활쓰레기배출방법', '')}<br>
    <b>♻️ 재활용:</b> {row.get('재활용품배출방법', '')}<br>
    <b>📅 배출요일:</b> {row.get('생활쓰레기배출요일', '')}<br>
    <b>📊 배출량:</b> {row.get('배출량', '')}<br>
    <b>📞 연락처:</b> {row.get('관리부서전화번호', '')}
    """

    color = get_color(row.get("배출량"))

    folium.CircleMarker(
        location=[row["위도"], row["경도"]],
        radius=6,
        color=color,
        fill=True,
        fill_opacity=0.7,
        popup=folium.Popup(popup_html, max_width=300)
    ).add_to(m)


# -----------------------------
# 📌 지도 출력
# -----------------------------
st_folium(m, width=1200, height=700)


# -----------------------------
# 📊 데이터 확인
# -----------------------------
with st.expander("📊 데이터 보기"):
    st.dataframe(df)
