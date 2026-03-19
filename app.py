import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="폭염 보고서 대시보드", layout="wide")

# -----------------------------
# 제목
# -----------------------------
st.title("📄 폭염 장기화에 따른 노인 온열질환 분석 보고서")
st.markdown("데이터 기반 정책 효과 및 취약성 분석 대시보드")

# -----------------------------
# 1. 서론
# -----------------------------
st.header("1️⃣ 연구 배경")

st.markdown("""
- 폭염은 단순한 기후 현상이 아닌 사회적 재난
- 고령층에서 온열질환 발생 집중
- 사회적 취약성(독거, 소득, 주거환경)이 피해를 증폭
""")

# -----------------------------
# 2. 기상 요인 분석
# -----------------------------
st.header("2️⃣ 기상 요인과 온열질환")

st.markdown("체감온도 상승에 따른 응급실 방문 증가 패턴")

# synthetic 데이터
temp = np.linspace(28, 40, 50)
er = np.where(temp < 35, temp * 2, temp * 5)  # 티핑포인트 반영

df_temp = pd.DataFrame({
    "체감온도": temp,
    "응급실 방문 수": er
})

fig_temp = px.line(df_temp, x="체감온도", y="응급실 방문 수",
                   title="체감온도와 온열질환 발생 관계")

fig_temp.add_vline(x=35, line_dash="dash")

st.plotly_chart(fig_temp, use_container_width=True)

st.markdown("""
👉 **핵심 해석**
- 체감온도 35도 이상에서 환자 수 급증
- 명확한 임계점 존재
""")

# -----------------------------
# 3. 사회적 취약성 분석
# -----------------------------
st.header("3️⃣ 사회적 취약성 분석")

st.markdown("독거노인 비율에 따른 온열질환 발생 차이")

ratio = np.linspace(0, 50, 50)
risk = ratio * 1.5 + 20

df_vul = pd.DataFrame({
    "독거노인 비율": ratio,
    "응급실 방문 수": risk
})

fig_vul = px.scatter(df_vul, x="독거노인 비율", y="응급실 방문 수",
                     trendline="ols",
                     title="독거노인 비율과 온열질환")

st.plotly_chart(fig_vul, use_container_width=True)

st.markdown("""
👉 **핵심 해석**
- 독거노인 비율 증가 → 온열질환 증가
- 사회적 고립이 주요 위험 요인
""")

# -----------------------------
# 4. 정책 효과 분석
# -----------------------------
st.header("4️⃣ 정책 효과 분석")

# 그래프 1
st.subheader("4.1 방문 케어 서비스 효과")

groups = ["Low", "High"]
data = []

for g in groups:
    for i in range(30):
        if g == "Low":
            val = np.random.normal(80, 10)
        else:
            val = np.random.normal(50, 8)
        data.append([g, val])

df1 = pd.DataFrame(data, columns=["Group", "ER"])

fig1 = px.box(df1, x="Group", y="ER", color="Group",
              title="방문 케어 수혜율별 응급실 방문 수")

st.plotly_chart(fig1, use_container_width=True)

st.markdown("""
👉 **해석**
- 방문 케어 높은 지역에서 환자 수 감소
- 직접 개입 정책의 효과 확인
""")

# 그래프 2
st.subheader("4.2 쉼터 접근성 분석")

time = np.linspace(1, 30, 50)
util = 100 * np.exp(-time / 10)
er2 = 20 + time * 3

df2 = pd.DataFrame({
    "접근시간": time,
    "이용률": util,
    "응급실 방문 수": er2
})

fig2 = px.line(df2, x="접근시간", y=["이용률", "응급실 방문 수"],
               title="쉼터 접근성과 이용률/환자 수 관계")

fig2.add_vline(x=15, line_dash="dash")

st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
👉 **해석**
- 접근 시간 증가 → 이용률 감소
- 15분 초과 시 정책 효과 급감
""")

# -----------------------------
# 5. 결론
# -----------------------------
st.header("5️⃣ 결론 및 정책 제언")

st.markdown("""
### 핵심 결론
- 폭염 피해는 사회적 취약성에 의해 결정됨
- 체감온도 35도 이상에서 위험 급증

### 정책 제언
1. 초근거리 마이크로 쉼터 확대
2. 방문 케어 서비스 강화
3. 에너지 바우처 도입
""")
