import plotly.express as px

# -----------------------------
# 간단 시각화 (확대 가능)
# -----------------------------
st.subheader("📊 변수 영향 시각화 (확대/줌 가능)")

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

fig = px.bar(
    data,
    x="요인",
    y="기여도",
    title="위험 요인별 기여도"
)

fig.update_layout(
    dragmode="zoom"  # 기본 줌 모드
)

st.plotly_chart(fig, use_container_width=True)
