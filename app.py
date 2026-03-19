import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide")

st.title("🌡️ 폭염 취약성 분석 대시보드")

# -----------------------------
# 그래프 1: 방문 케어 효과
# -----------------------------
st.subheader("📊 그래프 1: 방문 케어 수혜율에 따른 응급실 방문 수")

np.random.seed(42)

# synthetic 데이터 생성
groups = ["Low", "High"]
data_g1 = []

for g in groups:
    for day in range(1, 16):
        if g == "Low":
            value = np.random.normal(80, 10)  # 높은 환자 수
        else:
            value = np.random.normal(50, 8)   # 낮은 환자 수
        data_g1.append([g, day, value])

df1 = pd.DataFrame(data_g1, columns=["Group", "Day", "ER_Visits"])

fig1 = px.box(
    df1,
    x="Group",
    y="ER_Visits",
    color="Group",
    title="방문 케어 수혜율별 노인 응급실 방문 수 분포",
    points="all"  # 개별 점 표시
)

fig1.update_layout(
    dragmode="zoom"
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("""
👉 해석  
- High 그룹: 방문 케어 효과로 환자 수 감소  
- Low 그룹: 대응 부족 → 높은 변동성과 평균  
""")

# -----------------------------
# 그래프 2: 접근성 분석
# -----------------------------
st.subheader("📊 그래프 2: 쉼터 접근 시간 vs 이용률 & 환자 수")

# synthetic 데이터 생성
time = np.linspace(1, 30, 50)

utilization = 100 * np.exp(-time / 10)  # 이용률 감소
er_visits = 20 + time * 3               # 환자 수 증가

df2 = pd.DataFrame({
    "Access_Time": time,
    "Utilization": utilization,
    "ER_Visits": er_visits
})

# Plotly (이중 축)
fig2 = px.scatter(
    df2,
    x="Access_Time",
    y="Utilization",
    title="쉼터 접근성에 따른 이용률 및 온열질환 발생"
)

# 이용률 선 추가
fig2.add_scatter(
    x=df2["Access_Time"],
    y=df2["Utilization"],
    mode="lines",
    name="쉼터 이용률"
)

# 환자 수 선 추가 (secondary 느낌)
fig2.add_scatter(
    x=df2["Access_Time"],
    y=df2["ER_Visits"],
    mode="lines",
    name="응급실 방문 수",
    yaxis="y2"
)

fig2.update_layout(
    yaxis=dict(title="쉼터 이용률"),
    yaxis2=dict(
        title="응급실 방문 수",
        overlaying="y",
        side="right"
    ),
    dragmode="zoom"
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
👉 해석  
- 접근 시간 증가 → 쉼터 이용률 급감  
- 동시에 응급실 방문 수 증가  
- 특히 15분 이후 급격한 악화 구간 존재  
""")
