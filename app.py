import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────
st.set_page_config(
    page_title="폭염 온열질환 대시보드",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────
# iPhone Weather App Style CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background: linear-gradient(160deg, #1a3a5c 0%, #1e5799 30%, #2a7fcb 60%, #3d9bde 100%);
    min-height: 100vh;
}

/* ── Hide default Streamlit elements ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2rem 2rem 2rem 2rem !important;
    max-width: 1200px;
}

/* ── Hero Section ── */
.hero-card {
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 28px;
    padding: 2.5rem 2rem 2rem;
    margin-bottom: 1.5rem;
    text-align: center;
    animation: fadeSlideDown 0.7s ease forwards;
    position: relative;
    overflow: hidden;
}
.hero-card::before {
    content: '';
    position: absolute;
    top: -40%;
    left: -20%;
    width: 140%;
    height: 200%;
    background: radial-gradient(ellipse, rgba(255,200,100,0.15) 0%, transparent 60%);
    pointer-events: none;
}
.hero-title {
    font-size: clamp(1.1rem, 2vw, 1.3rem);
    font-weight: 500;
    color: rgba(255,255,255,0.75);
    letter-spacing: 0.08em;
    margin-bottom: 0.3rem;
}
.hero-temp {
    font-size: clamp(4rem, 10vw, 7rem);
    font-weight: 200;
    color: #fff;
    line-height: 1;
    margin: 0.2rem 0;
    letter-spacing: -0.03em;
    text-shadow: 0 4px 30px rgba(0,0,0,0.3);
}
.hero-condition {
    font-size: clamp(1.2rem, 2.5vw, 1.6rem);
    font-weight: 400;
    color: rgba(255,255,255,0.9);
    margin-bottom: 0.8rem;
}
.hero-range {
    font-size: 1rem;
    color: rgba(255,255,255,0.65);
    letter-spacing: 0.05em;
}
.hero-badge {
    display: inline-block;
    background: rgba(255, 80, 60, 0.85);
    color: white;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.8rem;
    animation: pulse-badge 2s infinite;
}
@keyframes pulse-badge {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255,80,60,0.5); }
    50% { box-shadow: 0 0 0 8px rgba(255,80,60,0); }
}

/* ── Stat Strip ── */
.stat-strip {
    background: rgba(255,255,255,0.10);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-around;
    animation: fadeSlideDown 0.8s ease forwards;
}
.stat-item {
    text-align: center;
    flex: 1;
    border-right: 1px solid rgba(255,255,255,0.2);
    padding: 0 0.5rem;
}
.stat-item:last-child { border-right: none; }
.stat-label {
    font-size: 0.65rem;
    font-weight: 600;
    color: rgba(255,255,255,0.55);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.2rem;
}
.stat-value {
    font-size: 1.3rem;
    font-weight: 500;
    color: #fff;
}
.stat-sub {
    font-size: 0.65rem;
    color: rgba(255,255,255,0.5);
}

/* ── Glass Card ── */
.glass-card {
    background: rgba(255,255,255,0.10);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 22px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
    animation: fadeSlideUp 0.6s ease forwards;
    position: relative;
    overflow: hidden;
}
.glass-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
}
.card-header {
    font-size: 0.7rem;
    font-weight: 600;
    color: rgba(255,255,255,0.55);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.card-header .icon { font-size: 0.9rem; }

/* ── Forecast Row (hourly-style) ── */
.forecast-row {
    display: flex;
    gap: 0.6rem;
    overflow-x: auto;
    padding-bottom: 0.3rem;
    scrollbar-width: none;
}
.forecast-row::-webkit-scrollbar { display: none; }
.forecast-item {
    flex: 0 0 auto;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 16px;
    padding: 0.6rem 0.9rem;
    text-align: center;
    min-width: 65px;
    transition: background 0.2s;
}
.forecast-item.active {
    background: rgba(255,255,255,0.22);
    border-color: rgba(255,255,255,0.4);
}
.forecast-time {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.6);
    margin-bottom: 0.3rem;
}
.forecast-icon { font-size: 1.2rem; margin: 0.2rem 0; }
.forecast-temp {
    font-size: 0.9rem;
    font-weight: 600;
    color: #fff;
}

/* ── Alert Banner ── */
.alert-banner {
    background: linear-gradient(135deg, rgba(255,80,60,0.35), rgba(255,140,0,0.35));
    border: 1px solid rgba(255,120,80,0.5);
    border-radius: 18px;
    padding: 1rem 1.4rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
    animation: fadeSlideUp 0.5s ease forwards;
}
.alert-icon { font-size: 2rem; }
.alert-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 0.2rem;
}
.alert-body {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.75);
    line-height: 1.5;
}

/* ── Policy Row (daily forecast style) ── */
.policy-row {
    display: flex;
    align-items: center;
    padding: 0.65rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}
.policy-row:last-child { border-bottom: none; }
.policy-name {
    flex: 1.5;
    font-size: 0.85rem;
    color: rgba(255,255,255,0.9);
    font-weight: 500;
}
.policy-bar-wrap {
    flex: 3;
    height: 6px;
    background: rgba(255,255,255,0.15);
    border-radius: 3px;
    overflow: hidden;
    margin: 0 0.8rem;
}
.policy-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 1s ease;
}
.policy-effect {
    flex: 0.8;
    text-align: right;
    font-size: 0.8rem;
    font-weight: 600;
    color: #fff;
}

/* ── Animations ── */
@keyframes fadeSlideDown {
    from { opacity: 0; transform: translateY(-18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Section Title ── */
.section-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: rgba(255,255,255,0.95);
    margin: 1.5rem 0 0.8rem;
    letter-spacing: -0.01em;
}

/* ── Plotly chart bg override ── */
.js-plotly-plot .plotly { background: transparent !important; }

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# Synthetic Data Generation
# ─────────────────────────────────────────
np.random.seed(42)
days = np.arange(1, 32)
temp = 28 + 6 * np.sin((days - 8) * np.pi / 16) + np.random.normal(0, 0.6, 31)
feels_like = temp + 2.5 + np.random.normal(0, 0.5, 31)
er_visits = np.where(feels_like < 35, feels_like * 1.8, feels_like * 5.5) + np.random.normal(0, 4, 31)
er_visits = np.clip(er_visits, 30, None)

regions = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "경기", "강원", "충북",
           "충남", "전북", "전남", "경북", "경남", "제주", "세종"]
elderly_ratio = np.array([18, 22, 20, 17, 21, 19, 20, 16, 28, 25, 26, 27, 31, 28, 25, 23, 15])
er_rate = elderly_ratio * 1.5 + 20 + np.random.normal(0, 5, len(regions))

shelter_access = np.linspace(5, 30, 50)
util_rate = 95 * np.exp(-shelter_access / 12) + np.random.normal(0, 2, 50)
er_shelter = 18 + shelter_access * 2.8 + np.random.normal(0, 3, 50)

# ─────────────────────────────────────────
# HERO SECTION
# ─────────────────────────────────────────
peak_temp = int(max(feels_like))
avg_temp = int(np.mean(temp))

st.markdown(f"""
<div class="hero-card">
    <div class="hero-title">🇰🇷 대한민국 · 2024년 8월</div>
    <div class="hero-temp">{peak_temp}°</div>
    <div class="hero-condition">폭염 특보 발효 중</div>
    <div class="hero-range">최저 {int(min(temp))}° · 최고 {peak_temp}° · 평균 체감 {avg_temp}°</div>
    <div class="hero-badge">🔴 온열질환 위험 VERY HIGH</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# STAT STRIP
# ─────────────────────────────────────────
total_er = int(sum(er_visits))
peak_day = days[np.argmax(er_visits)]
tipping_days = int(sum(feels_like >= 35))
high_risk_regions = int(sum(elderly_ratio >= 25))

st.markdown(f"""
<div class="stat-strip">
    <div class="stat-item">
        <div class="stat-label">💧 습도</div>
        <div class="stat-value">72%</div>
        <div class="stat-sub">높음</div>
    </div>
    <div class="stat-item">
        <div class="stat-label">🔥 임계점 초과</div>
        <div class="stat-value">{tipping_days}일</div>
        <div class="stat-sub">35°C 이상</div>
    </div>
    <div class="stat-item">
        <div class="stat-label">🚑 누적 내원</div>
        <div class="stat-value">{total_er:,}</div>
        <div class="stat-sub">응급실 방문</div>
    </div>
    <div class="stat-item">
        <div class="stat-label">⚠️ 고위험 지역</div>
        <div class="stat-value">{high_risk_regions}</div>
        <div class="stat-sub">독거 비율 25%↑</div>
    </div>
    <div class="stat-item">
        <div class="stat-label">📅 피크일</div>
        <div class="stat-value">8/{peak_day}일</div>
        <div class="stat-sub">최다 내원</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# ALERT BANNER
# ─────────────────────────────────────────
st.markdown("""
<div class="alert-banner">
    <div class="alert-icon">🌡️</div>
    <div>
        <div class="alert-title">폭염 경보 — 임계점 35°C 도달 시 환자 수 급증</div>
        <div class="alert-body">8월 10~18일 체감온도 35도 초과 구간에서 응급실 방문 수 기하급수적 증가 확인.
        독거노인 밀집 지역에서 피해 1.5배 이상 집중. 야간 열대야 시 에너지빈곤층 취약성 극대화.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# HOURLY-STYLE: Temperature Timeline
# ─────────────────────────────────────────
st.markdown("""
<div class="glass-card">
    <div class="card-header"><span class="icon">📈</span> 8월 일별 체감온도 & 응급실 방문 추이</div>
""", unsafe_allow_html=True)

fig_timeline = go.Figure()

# ER Area
fig_timeline.add_trace(go.Scatter(
    x=days, y=er_visits,
    fill='tozeroy',
    fillcolor='rgba(255,120,60,0.18)',
    line=dict(color='rgba(255,120,60,0.7)', width=2),
    name='응급실 방문수',
    yaxis='y2',
    hovertemplate='%{y:.0f}명<extra>응급실 방문</extra>',
))

# Temp Line
fig_timeline.add_trace(go.Scatter(
    x=days, y=feels_like,
    mode='lines+markers',
    line=dict(color='rgba(255,220,80,0.95)', width=2.5, shape='spline'),
    marker=dict(
        size=[10 if f >= 35 else 5 for f in feels_like],
        color=['#ff4444' if f >= 35 else 'rgba(255,220,80,0.8)' for f in feels_like],
        line=dict(color='white', width=1)
    ),
    name='체감온도(°C)',
    hovertemplate='%{y:.1f}°C<extra>체감온도</extra>',
))

# Tipping point line
fig_timeline.add_hline(
    y=35, line_dash='dot',
    line_color='rgba(255,80,60,0.6)', line_width=1.5,
    annotation_text='임계점 35°C',
    annotation_font_color='rgba(255,120,80,0.9)',
    annotation_font_size=11,
)

fig_timeline.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=10, r=10, t=10, b=30),
    height=240,
    showlegend=True,
    legend=dict(
        orientation='h', x=0.5, xanchor='center', y=1.12,
        font=dict(color='rgba(255,255,255,0.7)', size=11),
        bgcolor='rgba(0,0,0,0)',
    ),
    xaxis=dict(
        title='8월 (일)', title_font=dict(color='rgba(255,255,255,0.5)', size=11),
        tickfont=dict(color='rgba(255,255,255,0.6)', size=10),
        gridcolor='rgba(255,255,255,0.06)', showgrid=True,
        zeroline=False,
    ),
    yaxis=dict(
        title='체감온도 (°C)',
        title_font=dict(color='rgba(255,220,80,0.7)', size=10),
        tickfont=dict(color='rgba(255,255,255,0.5)', size=10),
        gridcolor='rgba(255,255,255,0.06)',
        range=[25, 42],
    ),
    yaxis2=dict(
        title='응급실 방문 수',
        title_font=dict(color='rgba(255,120,60,0.7)', size=10),
        tickfont=dict(color='rgba(255,255,255,0.5)', size=10),
        overlaying='y', side='right',
        gridcolor='rgba(0,0,0,0)',
    ),
    hovermode='x unified',
)
st.plotly_chart(fig_timeline, use_container_width=True, config={'displayModeBar': False})
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# TWO COLUMNS: Vulnerability + Map
# ─────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.markdown("""
    <div class="glass-card" style="height:360px">
        <div class="card-header"><span class="icon">👴</span> 독거노인 비율 vs 온열질환</div>
    """, unsafe_allow_html=True)

    fig_vul = go.Figure()
    colors = ['#ff4444' if r >= 25 else '#ffdc50' if r >= 20 else 'rgba(255,255,255,0.6)' for r in elderly_ratio]

    fig_vul.add_trace(go.Scatter(
        x=elderly_ratio, y=er_rate,
        mode='markers+text',
        marker=dict(size=14, color=colors, line=dict(color='rgba(255,255,255,0.4)', width=1.5),
                    opacity=0.9),
        text=regions,
        textposition='top center',
        textfont=dict(color='rgba(255,255,255,0.75)', size=9),
        hovertemplate='%{text}<br>독거 %{x:.0f}%<br>응급실 %{y:.0f}명<extra></extra>',
    ))

    m, b = np.polyfit(elderly_ratio, er_rate, 1)
    x_line = np.linspace(min(elderly_ratio), max(elderly_ratio), 50)
    fig_vul.add_trace(go.Scatter(
        x=x_line, y=m * x_line + b,
        mode='lines',
        line=dict(color='rgba(255,180,60,0.5)', width=1.5, dash='dash'),
        showlegend=False,
    ))

    fig_vul.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=35), height=270, showlegend=False,
        xaxis=dict(title='독거노인 비율 (%)', title_font=dict(color='rgba(255,255,255,0.5)', size=10),
                   tickfont=dict(color='rgba(255,255,255,0.55)', size=9),
                   gridcolor='rgba(255,255,255,0.07)', zeroline=False),
        yaxis=dict(title='응급실 방문 수', title_font=dict(color='rgba(255,255,255,0.5)', size=10),
                   tickfont=dict(color='rgba(255,255,255,0.55)', size=9),
                   gridcolor='rgba(255,255,255,0.07)'),
        hovermode='closest',
    )
    st.plotly_chart(fig_vul, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="glass-card" style="height:360px">
        <div class="card-header"><span class="icon">🗺️</span> 지역별 응급실 방문 강도</div>
    """, unsafe_allow_html=True)

    fig_bar = go.Figure()
    sorted_idx = np.argsort(er_rate)[::-1]
    bar_colors = ['#ff4444' if er_rate[i] > 65 else '#ffaa33' if er_rate[i] > 50 else 'rgba(255,255,255,0.45)'
                  for i in sorted_idx]

    fig_bar.add_trace(go.Bar(
        x=[regions[i] for i in sorted_idx],
        y=[er_rate[i] for i in sorted_idx],
        marker=dict(
            color=bar_colors,
            line=dict(color='rgba(255,255,255,0.0)', width=0),
            opacity=0.85,
        ),
        hovertemplate='%{x}<br>%{y:.0f}명<extra></extra>',
    ))

    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=5, r=5, t=10, b=35), height=270, showlegend=False,
        xaxis=dict(tickfont=dict(color='rgba(255,255,255,0.6)', size=9),
                   gridcolor='rgba(0,0,0,0)', zeroline=False),
        yaxis=dict(title='방문 수', title_font=dict(color='rgba(255,255,255,0.5)', size=10),
                   tickfont=dict(color='rgba(255,255,255,0.55)', size=9),
                   gridcolor='rgba(255,255,255,0.07)'),
        bargap=0.3,
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# POLICY EFFECTIVENESS (Daily-forecast style)
# ─────────────────────────────────────────
st.markdown("""
<div class="glass-card">
    <div class="card-header"><span class="icon">🏛️</span> 정책 효과 분석 — 저감 효과 비교</div>
    <div class="policy-row">
        <div class="policy-name">🏠 방문 케어 서비스</div>
        <div class="policy-bar-wrap">
            <div class="policy-bar-fill" style="width:82%; background:linear-gradient(90deg,#34c759,#30d158)"></div>
        </div>
        <div class="policy-effect">–37% 감소</div>
    </div>
    <div class="policy-row">
        <div class="policy-name">❄️ 무더위 쉼터 (15분↓)</div>
        <div class="policy-bar-wrap">
            <div class="policy-bar-fill" style="width:68%; background:linear-gradient(90deg,#30b0c7,#32ade6)"></div>
        </div>
        <div class="policy-effect">–28% 감소</div>
    </div>
    <div class="policy-row">
        <div class="policy-name">💸 에너지 바우처</div>
        <div class="policy-bar-wrap">
            <div class="policy-bar-fill" style="width:52%; background:linear-gradient(90deg,#ff9f0a,#ffcc02)"></div>
        </div>
        <div class="policy-effect">–21% 감소</div>
    </div>
    <div class="policy-row">
        <div class="policy-name">🔔 조기경보 문자</div>
        <div class="policy-bar-wrap">
            <div class="policy-bar-fill" style="width:35%; background:linear-gradient(90deg,#bf5af2,#9b59b6)"></div>
        </div>
        <div class="policy-effect">–12% 감소</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SHELTER ACCESS CHART
# ─────────────────────────────────────────
st.markdown("""
<div class="glass-card">
    <div class="card-header"><span class="icon">🏃</span> 쉼터 접근 시간 vs 이용률 / 응급실 방문 수</div>
""", unsafe_allow_html=True)

fig_shelter = go.Figure()

fig_shelter.add_trace(go.Scatter(
    x=shelter_access, y=util_rate,
    fill='tozeroy',
    fillcolor='rgba(52,199,89,0.15)',
    line=dict(color='rgba(52,199,89,0.85)', width=2, shape='spline'),
    name='쉼터 이용률(%)',
    hovertemplate='접근 %{x:.0f}분 → 이용률 %{y:.1f}%<extra></extra>',
))

fig_shelter.add_trace(go.Scatter(
    x=shelter_access, y=er_shelter,
    mode='lines',
    line=dict(color='rgba(255,120,60,0.85)', width=2, shape='spline'),
    name='응급실 방문 수',
    yaxis='y2',
    hovertemplate='접근 %{x:.0f}분 → %{y:.0f}명<extra></extra>',
))

fig_shelter.add_vline(
    x=15, line_dash='dot',
    line_color='rgba(255,220,80,0.7)', line_width=1.5,
    annotation_text='효과 임계점 15분',
    annotation_font_color='rgba(255,220,80,0.9)',
    annotation_font_size=11,
)

fig_shelter.update_layout(
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=10, r=10, t=10, b=35), height=220, showlegend=True,
    legend=dict(orientation='h', x=0.5, xanchor='center', y=1.15,
                font=dict(color='rgba(255,255,255,0.7)', size=11),
                bgcolor='rgba(0,0,0,0)'),
    xaxis=dict(title='쉼터 접근 시간 (분)', title_font=dict(color='rgba(255,255,255,0.5)', size=10),
               tickfont=dict(color='rgba(255,255,255,0.55)', size=9),
               gridcolor='rgba(255,255,255,0.07)', zeroline=False),
    yaxis=dict(title='이용률 (%)', title_font=dict(color='rgba(52,199,89,0.7)', size=10),
               tickfont=dict(color='rgba(255,255,255,0.5)', size=9),
               gridcolor='rgba(255,255,255,0.07)'),
    yaxis2=dict(title='응급실 방문 수', title_font=dict(color='rgba(255,120,60,0.7)', size=10),
                tickfont=dict(color='rgba(255,255,255,0.5)', size=9),
                overlaying='y', side='right', gridcolor='rgba(0,0,0,0)'),
    hovermode='x unified',
)
st.plotly_chart(fig_shelter, use_container_width=True, config={'displayModeBar': False})
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# CONCLUSION CARDS (iPhone-style tiles)
# ─────────────────────────────────────────
st.markdown("""<div class="section-title">📋 핵심 결론 & 정책 제언</div>""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="medium")
conclusions = [
    ("🌡️", "임계점 관리", "체감온도 35°C 초과 시\n환자 수 기하급수적 폭증.\n폭염 특보 초기 48시간\n집중 대응 필요."),
    ("👴", "취약계층 집중", "독거노인 비율 25% 이상\n지역에서 피해 1.5배 증가.\n사회적 고립이 핵심 위험 요인."),
    ("❄️", "인프라 접근성", "쉼터 15분 초과 시\n이용률 급감·환자 급증.\n마이크로 쉼터 확대 시급."),
]
for col, (icon, title, body) in zip([c1, c2, c3], conclusions):
    with col:
        st.markdown(f"""
        <div class="glass-card" style="min-height:150px; text-align:center">
            <div style="font-size:2rem; margin-bottom:0.5rem">{icon}</div>
            <div style="font-size:0.85rem; font-weight:700; color:#fff; margin-bottom:0.5rem">{title}</div>
            <div style="font-size:0.75rem; color:rgba(255,255,255,0.65); line-height:1.6; white-space:pre-line">{body}</div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center; padding:1.5rem 0 0.5rem; color:rgba(255,255,255,0.3); font-size:0.7rem; letter-spacing:0.05em;">
    폭염 장기화에 따른 노인 온열질환 분석 보고서 · 2024년 8월 가상 데이터 기반
</div>
""", unsafe_allow_html=True)
