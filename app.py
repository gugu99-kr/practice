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
KAKAO_API_KEY = "여기에_API_KEY_입력"

# -----------------------------
# 📍 주소 → 좌표 변환
# -----------------------------
def get_lat_lon(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}

    try:
        res = requests.get(url, headers=headers, params=params)
        result = res.json()

        if result['documents']:
            return float(result['documents'][0]['y']), float(result['documents'][0]['x'])
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
    st.warning("👉 CSV + 엑셀 파일 모두 업로드하세요")
    st.stop()

df = pd.read_csv(uploaded_csv, encoding="cp949")

# -----------------------------
# 📊 엑셀 헤더 자동 찾기
# -----------------------------
df_stat_raw = pd.read_excel(uploaded_excel, header=None)

header_row = None
for i in range(len(df_stat_raw)):
    row = df_stat_raw.iloc[i].astype(str)
    if row.str.contains("구").any():
        header_row = i
        break

if header_row is None:
    st.error("❌ 엑셀 헤더 행 찾기 실패")
    st.write(df_stat_raw.head(10))
    st.stop()

df_stat = pd.read_excel(uploaded_excel, header=header_row)


# -----------------------------
# 🔍 컬럼 자동 탐색
# -----------------------------
def find_gu_column(columns):
    for col in columns:
        if "구" in col:
            return col
    return None

def find_value_column(columns):
    for col in columns:
        if "합계" in col or "총" in col or "발생" in col:
            return col
    return None

csv_gu_col = find_gu_column(df.columns)
excel_gu_col = find_gu_column(df_stat.columns)
value_col = find_value_column(df_stat.columns)

if csv_gu_col is None or excel_gu_col is None:
    st.error("❌ 시군구 컬럼 찾기 실패")
    st.write("CSV:", df.columns)
    st.write("엑셀:", df_stat.columns)
    st.stop()

if value_col is None:
    st.error("❌ 배출량 컬럼 찾기 실패")
    st.write("엑셀:", df_stat.columns)
    st.stop()

# -----------------------------
# 📌 컬럼 통일
# -----------------------------
df = df.rename(columns={csv_gu_col: "시군구명"})
df_stat = df_stat.rename(columns={
    excel_gu_col: "시군구명",
    value_col: "배출량"
})

# -----------------------------
# 🧹 데이터 정리
# -----------------------------
df["시군구명"] = df["시군구명"].astype(str).str.replace("구", "").str.strip()
df_stat["시군구명"] = df_stat["시군구명"].astype(str).str.replace("구", "").str.strip()

df_stat["배출량"] = pd.to_numeric(df_stat["배출량"], errors="coerce")
df_stat = df_stat[["시군구명", "배출량"]]

# -----------------------------
# 🔗 merge
# -----------------------------
df = df.merge(df_stat, on="시군구명", how="left")

# -----------------------------
# 📍 주소 컬럼 자동 찾기
# -----------------------------
address_col = None
for col in df.columns:
    if "주소" in col or "위치" in col or "장소" in col:
        address_col = col
        break

if address_col is None:
    st.error("❌ 주소 컬럼 찾기 실패")
    st.write(df.columns)
    st.stop()

# -----------------------------
# 📍 좌표 생성
# -----------------------------
if "위도" not in df.columns or "경도" not in df.columns:

    st.warning("⏳ 좌표 생성 중... (시간 소요)")

    lat_list = []
    lon_list = []

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

gu_list = sorted(df["시군구명"].dropna().unique())
selected_gu = st.sidebar.selectbox("자치구 선택", ["전체"] + list(gu_list))

if selected_gu != "전체":
    df = df[df["시군구명"] == selected_gu]


# -----------------------------
# 🎨 색상 함수
# -----------------------------
def get_color(v):
    if pd.isna(v):
        return "gray"
    elif v > 1000:
        return "red"
    elif v > 500:
        return "orange"
    else:
        return "green"


# -----------------------------
# 🗺️ 지도 생성
# -----------------------------
m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)

for _, row in df.iterrows():

    if pd.isna(row["위도"]) or pd.isna(row["경도"]):
        continue

    popup_html = f"""
    <b>📍 장소:</b> {row.get(address_col, '')}<br>
    <b>🗑️ 배출방법:</b> {row.get('생활쓰레기배출방법', '')}<br>
    <b>♻️ 재활용:</b> {row.get('재활용품배출방법', '')}<br>
    <b>📅 요일:</b> {row.get('생활쓰레기배출요일', '')}<br>
    <b>📊 배출량:</b> {row.get('배출량', '')}
    """

    folium.CircleMarker(
        location=[row["위도"], row["경도"]],
        radius=6,
        color=get_color(row["배출량"]),
        fill=True,
        fill_opacity=0.7,
        popup=folium.Popup(popup_html, max_width=300)
    ).add_to(m)

st_folium(m, width=1200, height=700)

# -----------------------------
# 📊 데이터 확인
# -----------------------------
with st.expander("📊 데이터 보기"):
    st.dataframe(df)
