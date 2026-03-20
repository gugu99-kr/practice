import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ──────────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="생활쓰레기 배출 현황",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0d1117; }
[data-testid="stSidebar"]          { background: #161b22; }
.block-container { padding-top: 1rem; }
h1,h2,h3,h4 { color: #e6edf3; }
.metric-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 12px; padding: 14px 18px; text-align: center;
}
.metric-val   { font-size: 1.5rem; font-weight: 700; color: #58a6ff; }
.metric-label { font-size: .76rem; color: #8b949e; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 서울 25개 구 좌표
# ──────────────────────────────────────────────
GU_COORDS = {
    "종로구": (37.5730, 126.9794), "중구":     (37.5640, 126.9975),
    "용산구": (37.5324, 126.9904), "성동구":   (37.5636, 127.0368),
    "광진구": (37.5384, 127.0822), "동대문구": (37.5744, 127.0403),
    "중랑구": (37.6063, 127.0928), "성북구":   (37.5894, 127.0167),
    "강북구": (37.6397, 127.0258), "도봉구":   (37.6688, 127.0471),
    "노원구": (37.6542, 127.0568), "은평구":   (37.6176, 126.9227),
    "서대문구":(37.5791,126.9368), "마포구":   (37.5663, 126.9019),
    "양천구": (37.5170, 126.8665), "강서구":   (37.5509, 126.8495),
    "구로구": (37.4955, 126.8875), "금천구":   (37.4569, 126.8956),
    "영등포구":(37.5264,126.8963), "동작구":   (37.5124, 126.9393),
    "관악구": (37.4784, 126.9516), "서초구":   (37.4836, 127.0327),
    "강남구": (37.5172, 127.0473), "송파구":   (37.5145, 127.1059),
    "강동구": (37.5492, 127.1465),
}

COLOR_MAP = {"low": "#3fb950", "mid": "#d29922", "high": "#f85149"}
LABEL_MAP = {"low": "낮음",    "mid": "보통",    "high": "높음"}

# ──────────────────────────────────────────────
# 파일 경로 (app.py와 같은 폴더에 위치)
# ──────────────────────────────────────────────
XLSX_PATH = "02_01_2024_생활계폐기물_생활_가정___사업장비배출시설계__발생_및_처리현황.xlsx"
CSV_PATH  = "생활쓰레기배출정보.csv"

# ──────────────────────────────────────────────
# 데이터 로드
# ──────────────────────────────────────────────
@st.cache_data
def load_waste_volume() -> pd.DataFrame:
    raw = pd.read_excel(
        XLSX_PATH,
        sheet_name="2-나-1). (시군구) 생활(가정)폐기물 발생량",
        header=None,
    )
    records = []
    for _, row in raw.iterrows():
        sido, sigungu, category, value = row[0], row[1], row[2], row[5]
        if (sido == "서울"
                and sigungu not in [None, "소계"]
                and pd.notna(sigungu)
                and category == "합계"):
            try:
                records.append({"시군구명": sigungu, "발생량_톤": float(value)})
            except (ValueError, TypeError):
                pass
    return pd.DataFrame(records)


@st.cache_data
def load_disposal_info() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH, encoding="cp949")
    seoul = df[df["시도명"] == "서울특별시"].copy()
    seoul = seoul.drop_duplicates(subset="시군구명", keep="first")
    keep = [
        "시군구명", "배출장소", "생활쓰레기배출방법", "음식물쓰레기배출방법",
        "재활용품배출방법", "생활쓰레기배출요일", "음식물쓰레기배출요일",
        "재활용품배출요일", "생활쓰레기배출시작시각", "생활쓰레기배출종료시각",
        "관리부서명", "관리부서전화번호",
    ]
    return seoul[keep].reset_index(drop=True)


@st.cache_data
def build_dataset() -> pd.DataFrame:
    vol  = load_waste_volume()
    info = load_disposal_info()
    df   = pd.merge(vol, info, on="시군구명", how="left")

    q33 = df["발생량_톤"].quantile(0.33)
    q66 = df["발생량_톤"].quantile(0.66)
    df["레벨"] = df["발생량_톤"].apply(
        lambda v: "high" if v >= q66 else ("mid" if v >= q33 else "low")
    )
    df["lat"] = df["시군구명"].map(lambda x: GU_COORDS.get(x, (37.55, 126.97))[0])
    df["lng"] = df["시군구명"].map(lambda x: GU_COORDS.get(x, (37.55, 126.97))[1])
    return df


# ──────────────────────────────────────────────
# 지도 빌더
# ──────────────────────────────────────────────
def build_map(df: pd.DataFrame, selected: str | None = None) -> folium.Map:
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=11,
                   tiles="CartoDB dark_matter")

    for _, row in df.iterrows():
        color  = COLOR_MAP[row["레벨"]]
        gu     = row["시군구명"]
        is_sel = gu == selected

        s_time  = row.get("생활쓰레기배출시작시각", "–")
        e_time  = row.get("생활쓰레기배출종료시각", "–")
        method  = str(row.get("생활쓰레기배출방법",  "–"))[:55] + "…"
        food    = str(row.get("음식물쓰레기배출방법", "–"))[:55] + "…"
        recycle = str(row.get("재활용품배출방법",     "–"))[:55] + "…"

        popup_html = f"""
        <div style="font-family:sans-serif;min-width:270px;max-width:310px;
                    background:#161b22;color:#e6edf3;border-radius:12px;padding:16px;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;
                      border-bottom:1px solid #30363d;padding-bottom:10px;">
            <div style="width:36px;height:36px;border-radius:9px;
                        background:{color}22;color:{color};display:flex;
                        align-items:center;justify-content:center;
                        font-weight:700;font-size:.85rem;">{LABEL_MAP[row['레벨']]}</div>
            <div>
              <div style="font-size:1rem;font-weight:700;">{gu}</div>
              <div style="font-size:.72rem;color:#8b949e;">연간 {row['발생량_톤']:,.0f} 톤</div>
            </div>
          </div>
          <table style="width:100%;font-size:.75rem;border-collapse:collapse;">
            <tr><td style="color:#8b949e;padding:3px 0;white-space:nowrap;vertical-align:top;">📍 배출장소</td>
                <td style="padding:3px 6px;">{row.get('배출장소','–')}</td></tr>
            <tr><td style="color:#8b949e;padding:3px 0;white-space:nowrap;vertical-align:top;">🗑️ 배출방법</td>
                <td style="padding:3px 6px;">{method}</td></tr>
            <tr><td style="color:#8b949e;padding:3px 0;white-space:nowrap;vertical-align:top;">🥬 음식물</td>
                <td style="padding:3px 6px;">{food}</td></tr>
            <tr><td style="color:#8b949e;padding:3px 0;white-space:nowrap;vertical-align:top;">♻️ 재활용</td>
                <td style="padding:3px 6px;">{recycle}</td></tr>
            <tr><td style="color:#8b949e;padding:3px 0;white-space:nowrap;">📅 배출요일</td>
                <td style="padding:3px 6px;">{row.get('생활쓰레기배출요일','–')}</td></tr>
            <tr><td style="color:#8b949e;padding:3px 0;white-space:nowrap;">🕐 배출시간</td>
                <td style="padding:3px 6px;">{s_time} ~ {e_time}</td></tr>
          </table>
          <div style="margin-top:10px;padding-top:8px;border-top:1px solid #30363d;
                      display:flex;justify-content:space-between;font-size:.75rem;">
            <span style="color:#8b949e;">{row.get('관리부서명','청소행정과')}</span>
            <span style="color:#58a6ff;">{row.get('관리부서전화번호','–')}</span>
          </div>
        </div>"""

        folium.CircleMarker(
            location=[row["lat"], row["lng"]],
            radius=20 if is_sel else 15,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6 if is_sel else 0.35,
            weight=3 if is_sel else 1.5,
            tooltip=folium.Tooltip(f"<b>{gu}</b><br>{row['발생량_톤']:,.0f} 톤/년"),
            popup=folium.Popup(popup_html, max_width=330),
        ).add_to(m)

        folium.Marker(
            location=[row["lat"], row["lng"]],
            icon=folium.DivIcon(
                html=(f'<div style="font-size:.63rem;color:{color};white-space:nowrap;'
                      f'font-weight:600;text-shadow:0 0 4px #000;">{gu}</div>'),
                icon_size=(60, 20),
                icon_anchor=(30, -5),
            ),
        ).add_to(m)

    return m


# ──────────────────────────────────────────────
# 메인 UI
# ──────────────────────────────────────────────
df = build_dataset()

# 헤더
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("## ♻️ 서울시 생활쓰레기 배출 현황")
with col_h2:
    st.markdown(
        "<div style='display:flex;gap:14px;justify-content:flex-end;padding-top:10px;"
        "font-size:.82rem;'>🟢 낮음 &nbsp; 🟡 보통 &nbsp; 🔴 높음</div>",
        unsafe_allow_html=True,
    )

# 통계 카드
total  = df["발생량_톤"].sum()
avg    = df["발생량_톤"].mean()
top_gu = df.loc[df["발생량_톤"].idxmax(), "시군구명"]
low_gu = df.loc[df["발생량_톤"].idxmin(), "시군구명"]

for col, val, label in zip(
    st.columns(4),
    [f"{total:,.0f} 톤", f"{avg:,.0f} 톤", top_gu, low_gu],
    ["서울 총 발생량 (연간)", "구별 평균 발생량", "최고 배출 구", "최저 배출 구"],
):
    with col:
        st.markdown(
            f'<div class="metric-card"><div class="metric-val">{val}</div>'
            f'<div class="metric-label">{label}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.markdown("### 🏙️ 구 선택")
    selected_gu = st.selectbox(
        "구를 선택하면 우측에 상세정보가 표시됩니다",
        ["전체"] + sorted(df["시군구명"].tolist()),
    )

    st.markdown("---")
    st.markdown("### 📊 배출량 필터")
    level_filter = st.multiselect(
        "배출 수준",
        options=["low", "mid", "high"],
        default=["low", "mid", "high"],
        format_func=lambda x: {"low":"🟢 낮음","mid":"🟡 보통","high":"🔴 높음"}[x],
    )

    st.markdown("---")
    st.markdown("### 🗂️ 발생량 순위")
    rank_df = df[["시군구명","발생량_톤","레벨"]].sort_values("발생량_톤", ascending=False)
    for _, r in rank_df.iterrows():
        icon = {"low":"🟢","mid":"🟡","high":"🔴"}[r["레벨"]]
        st.markdown(f"{icon} **{r['시군구명']}** — {r['발생량_톤']:,.0f} 톤")

# 지도 + 상세 패널
map_col, detail_col = st.columns([2, 1])

filtered = df[df["레벨"].isin(level_filter)] if level_filter else df
sel = selected_gu if selected_gu != "전체" else None

with map_col:
    folium_map = build_map(filtered, sel)
    st_folium(folium_map, width=None, height=560, returned_objects=[])

with detail_col:
    st.markdown("#### 📋 배출 상세 정보")
    if selected_gu == "전체":
        st.info("사이드바에서 구를 선택하거나\n지도 마커를 클릭하세요.")
    else:
        row   = df[df["시군구명"] == selected_gu].iloc[0]
        color = COLOR_MAP[row["레벨"]]
        st.markdown(
            f"**{selected_gu}** &nbsp;"
            f"<span style='background:{color}22;color:{color};border-radius:6px;"
            f"padding:2px 8px;font-size:.8rem;'>{LABEL_MAP[row['레벨']]}</span>",
            unsafe_allow_html=True,
        )
        st.metric("연간 발생량", f"{row['발생량_톤']:,.0f} 톤")
        st.divider()

        field_map = {
            "📍 배출장소":            "배출장소",
            "🗑️ 생활쓰레기 배출방법": "생활쓰레기배출방법",
            "🥬 음식물 배출방법":      "음식물쓰레기배출방법",
            "♻️ 재활용 배출방법":      "재활용품배출방법",
            "📅 생활쓰레기 배출요일":  "생활쓰레기배출요일",
            "📅 음식물 배출요일":      "음식물쓰레기배출요일",
            "📅 재활용 배출요일":      "재활용품배출요일",
            "📞 관리부서":             "관리부서명",
            "☎️ 연락처":              "관리부서전화번호",
        }
        for label, key in field_map.items():
            val = row.get(key, "–")
            st.markdown(f"**{label}**")
            st.write("–" if pd.isna(val) else str(val))

        s = row.get("생활쓰레기배출시작시각", "–")
        e = row.get("생활쓰레기배출종료시각", "–")
        st.markdown("**🕐 배출 시간**")
        st.write(f"{s} ~ {e}")

# 하단 전체 테이블
with st.expander("📊 전체 데이터 테이블"):
    show = ["시군구명","발생량_톤","레벨","배출장소",
            "생활쓰레기배출요일","음식물쓰레기배출요일",
            "재활용품배출요일","관리부서전화번호"]
    tbl = df[[c for c in show if c in df.columns]].copy()
    tbl["레벨"] = tbl["레벨"].map(LABEL_MAP)
    tbl = tbl.sort_values("발생량_톤", ascending=False)
    st.dataframe(tbl, use_container_width=True, hide_index=True)
```

---

**requirements.txt**
```
streamlit==1.41.1
pandas==2.2.2
openpyxl==3.1.2
folium==0.17.0
streamlit-folium==0.23.1
```

---

**폴더 구조 참고**
```
프로젝트 폴더/
├── app.py
├── requirements.txt
├── 02_01_2024_생활계폐기물_...xlsx
└── 생활쓰레기배출정보.csv
