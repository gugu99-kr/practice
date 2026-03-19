import streamlit as st
import pandas as pd

st.set_page_config(page_title="폭염 취약성 분석 앱", layout="wide")

st.title("🌡️ 폭염 취약성 기반 온열질환 위험도 분석")
st.markdown("체감온도, 사회적 취약성, 정책 변수 기반 간단 시뮬레이션")

# -----------------------------
# 입력 영역
# -----------------------------
st.sidebar.header("📊 입력 변수")

temp = st.sidebar.slider("체감온도 (°C)", 28, 40, 33)
elderly_ratio = st.sidebar.slider("독거노인 비율 (%)", 0, 50, 20)
low_income_ratio = st.sidebar.slider("기초생활수급자 비율 (%)", 0, 50, 15)
shelter_time = st.sidebar.slider("쉼터 접근 시간 (분)", 1, 30, 10)
care_service = st.sidebar.selectbox("방문 케어 서비스", ["낮음", "높음"])

# -----------------------------
# 위험도 계산 로직 (간단 모델)
# -----------------------------
risk_score = 0

# 체감온도 영향 (티핑포인트 반영)
if temp < 33:
    risk_score += 1
elif temp < 35:
    risk_score += 3
else:
    risk_score += 6  # 임계점 이후 급증

# 사회적 취약성
risk_score += elderly_ratio * 0.05
risk_score += low_income_ratio * 0.04

# 접근성 (15분 기준)
if shelter_time > 15:
    risk_score += 3
else:
    risk_score -= 1

# 방문 케어 효과
if care_service == "높음":
    risk_score -= 3
else:
    risk_score += 2

# -----------------------------
# 위험도 레벨 분류
# -----------------------------
if risk_score < 5:
    level = "🟢 낮음"
elif risk_score < 10:
    level = "🟡 보통"
else:
    level = "🔴 높음"

# -----------------------------
# 결과 출력
# -----------------------------
st.subheader("📈 분석 결과")

col1, col2 = st.columns(2)

with col1:
    st.metric("위험 점수", round(risk_score, 2))
    st.metric("위험 수준", level)

with col2:
    st.write("### 🔍 해석")
    if temp >= 35:
        st.write("- 체감온도 임계점 도달 → 환자 급증 가능")
    if shelter_time > 15:
        st.write("- 쉼터 접근성 부족 → 정책 효과 저하")
    if care_service == "낮음":
        st.write("- 방문 케어 부족 → 위험 증가")

# -----------------------------
# 정책 제안
# -----------------------------
st.subheader("🧩 맞춤형 정책 제안")

if shelter_time > 15:
    st.write("✔ 초근거리 마이크로 쉼터 확대 필요")

if care_service == "낮음":
    st.write("✔ 방문 케어 서비스 강화 필요")

if low_income_ratio > 20:
    st.write("✔ 에너지 바우처 지원 필요")

if temp >= 35:
    st.write("✔ 폭염 경보 대응 체계 즉시 가동 필요")

# -----------------------------
# 간단 시각화
# -----------------------------
st.subheader("📊 변수 영향 시각화")

data = pd.DataFrame({
    "요인": ["체감온도", "독거노인", "저소득층", "접근성", "방문케어"],
    "기여도": [
        temp / 10,
        elderly_ratio / 10,
        low_income_ratio / 10,
        shelter_time / 10,
        -3 if care_service == "높음" else 2
    ]
})

st.bar_chart(data.set_index("요인"))
