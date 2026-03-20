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
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }
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
# 📊 CSV 데이터 로드
# -----------------------------
@st.cache_data
def load_main_data():
    df = pd.read_csv("생활쓰레기배출정보.csv", encoding="cp949")
    df = df[df["시도명"] == "서울특별시"]
    return df


# -----------------------------
# 📊 엑셀 통계 데이터 로드
# -----------------------------
@st.cache_data
def load_stat_data():
    df_stat = pd.read_excel("02_01_2024_생활계폐기물(생활(가정), 사업장비배출시설계) 발생 및 처리현황.xlsx")

    # 👉 필요시 컬럼 확인
    # st.write(df_stat.columns)

    df_stat = df_stat.rename(columns={
        "시군구": "시군구명",
        "합계": "배출량"
    })

    df_stat = df_stat[["시군구명", "배출량"]]
    df_stat["배출량"] = pd.to_numeric(df_stat["배출량"], errors="coerce")

    return df_stat


df = load_main_data()
df_stat = load_stat_data()

# -----------------------------
# 🔗 데이터 merge
# -----------------------------
df = df.merge(df_stat, on="시군구명", how="left")


# -----------------------------
# 📍 좌표 생성 (최초 1회만 실행 권장)
# -----------------------------
if "위도" not in df.columns or "경도" not in df.columns:

    st.warning("⏳ 좌표 생성 중... (최초 1회 오래 걸림)")

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

    # 👉 저장 (다음부터 빠르게)
    df.to_csv("좌표추가완료.csv", index=False, encoding="cp949")
    st.success("✅ 좌표 생성 완료! 다음부터는 저장된 파일 사용 추천")


# -----------------------------
# 🎛️ 필터 UI
# -----------------------------
st.sidebar.header("📌 필터")

gu_list = df["시군구명"].dropna().unique()
selected_gu = st.sidebar.selectbox("자치구 선택", ["전체"] + list(gu_list))

if selected_gu != "전체":
    df = df[df["시군구명"] == selected_gu]


# -----------------------------
# 🎨 색상 함수 (배출량 기준)
# -----------------------------
def get_color(volume):

    if pd.isna(volume):
        return "gray"

    if volume > 1000:
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

    if pd.isna(row["위도"]) or pd.isna(row["경도"]):
        continue

    popup_html = f"""
    <b>📍 배출장소:</b> {row['배출장소']}<br>
    <b>🗑️ 배출방법:</b> {row['생활쓰레기배출방법']}<br>
    <b>♻️ 재활용:</b> {row['재활용품배출방법']}<br>
    <b>📅 배출요일:</b> {row['생활쓰레기배출요일']}<br>
    <b>📊 배출량:</b> {row['배출량']}<br>
    <b>📞 연락처:</b> {row['관리부서전화번호']}
    """

    color = get_color(row["배출량"])

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
st_data = st_folium(m, width=1200, height=700)


# -----------------------------
# 📊 데이터 보기 (옵션)
# -----------------------------
with st.expander("📊 데이터 확인"):
    st.dataframe(df)
