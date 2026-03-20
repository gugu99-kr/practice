import re
import html
import pandas as pd
import streamlit as st

# 1. 페이지 설정
st.set_page_config(
    page_title="우리 구 쓰레기 배출 도우미",
    page_icon="🗑️",
    layout="wide"
)

# -----------------------------
# 스타일 (CSS)
# -----------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
.stApp { background: #f8fbff; color: #0f172a; }

.app-shell { max-width: 1100px; margin: 0 auto; padding: 20px; }

.hero-box {
    background: linear-gradient(135deg, #4f8cff 0%, #3b82f6 100%);
    padding: 35px; border-radius: 28px; color: white;
    box-shadow: 0 16px 30px rgba(59, 130, 246, 0.2);
    margin-bottom: 25px;
}

.card {
    background: white; border-radius: 26px; padding: 25px;
    border: 1px solid #e2e8f0; box-shadow: 0 10px 20px rgba(0,0,0,0.04);
    min-height: 400px; transition: transform 0.2s;
}
.card:hover { transform: translateY(-5px); }

.card-title { font-size: 1.3rem; font-weight: 800; margin-bottom: 20px; color: #1e293b; }
.label { font-size: 0.85rem; color: #64748b; font-weight: 700; margin-top: 18px; display: flex; align-items: center; gap: 5px; }

/* 요일 배지 디자인 수정 */
.day-container { display: flex; gap: 8px; margin-top: 10px; }
.day-dot {
    width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;
    border-radius: 10px; background: #f1f5f9; color: #94a3b8; font-size: 0.9rem; font-weight: 700;
    transition: all 0.3s;
}
.day-dot.active { background: #3b82f6; color: white; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3); }

.time-val { font-size: 1.2rem; font-weight: 800; color: #0f172a; margin-top: 5px; }
.place-tag {
    display: inline-block; background: #ecfdf5; color: #059669; 
    padding: 5px 12px; border-radius: 8px; font-weight: 700; font-size: 0.9rem; margin-top: 8px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------
# 유틸리티 함수
# -----------------------------
DAY_ORDER = ["월", "화", "수", "목", "금", "토", "일"]

def esc(val): return html.escape(str(val))

def clean_text(val):
    if pd.isna(val) or str(val).lower() == 'nan': return "정보 없음"
    t = str(val).strip()
    # 띄어쓰기 교정
    t = t.replace("집앞", "집 앞").replace("점포앞", "점포 앞").replace("건물앞", "건물 앞")
    return t

@st.cache_data
def load_data(path):
    for enc in ["cp949", "utf-8-sig", "utf-8"]:
        try:
            df = pd.read_csv(path, encoding=enc)
            df.columns = [c.strip().replace(" ", "") for c in df.columns]
            return df
        except: continue
    return None

# -----------------------------
# 카드 렌더링 (요일 오류 해결 버전)
# -----------------------------
def render_card(title, emoji, day_raw, row, prefix):
    # 1. 요일 판별 로직 (정규표현식으로 더 정확하게)
    day_str = str(day_raw)
    active_days = []
    for d in DAY_ORDER:
        if re.search(f"[{d}]", day_str): # '월', '화' 등이 문자열에 포함되어 있는지 확인
            active_days.append(d)
    
    days_html = "".join([
        f'<div class="day-dot {"active" if d in active_days else ""}">{d}</div>'
        for d in DAY_ORDER
    ])

    # 2. 시간 추출
    start = str(row.get(f"{prefix}쓰레기배출시작시각", row.get(f"{prefix}폐기물배출시작시각", ""))).strip()
    end = str(row.get(f"{prefix}쓰레기배출종료시각", row.get(f"{prefix}폐기물배출종료시각", ""))).strip()
    time_val = f"{start} ~ {end}" if start != "nan" and start else "시간 정보 없음"

    # 3. 방법/장소 추출
    method = clean_text(row.get(f"{prefix}쓰레기배출방법", row.get(f"{prefix}폐기물배출방법", "정보 없음")))
    p_type = clean_text(row.get("배출장소유형", "정보 없음"))
    p_val = clean_text(row.get("배출장소", "정보 없음"))

    st.markdown(f"""
        <div class="card">
            <div class="card-title">{emoji} {esc(title)}</div>
            
            <div class="label">🗓️ 배출 요일</div>
            <div class="day-container">{days_html}</div>
            
            <div class="label">⏰ 배출 시간</div>
            <div class="time-val">{esc(time_val)}</div>
            
            <div class="label">📝 배출 방법</div>
            <div class="value-text" style="font-weight:600; margin-top:4px;">{esc(method)}</div>
            
            <div class="label">📍 배출 장소 유형</div>
            <div class="place-tag">{esc(p_type)}</div>
            
            <div class="label">🏠 상세 장소</div>
            <div class="value-text" style="font-size:0.9rem; color:#64748b; margin-top:4px;">{esc(p_val)}</div>
        </div>
    """, unsafe_allow_html=True)

# -----------------------------
# 메인 실행
# -----------------------------
DATA_PATH = "생활쓰레기배출정보_서울특별시.csv"
df = load_data(DATA_PATH)

if df is not None:
    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    
    st.markdown('<div class="hero-box"><h1>🗑️ 우리 구 쓰레기 배출 도우미</h1><p>내 동네의 배출 요일과 시간을 정확하게 확인하세요.</p></div>', unsafe_allow_html=True)
    
    # 구 선택
    gu_col = next((c for c in ["시군구명", "자치구명", "구명"] if c in df.columns), df.columns[0])
    gu_list = sorted(df[gu_col].unique())
    selected_gu = st.selectbox("자치구를 선택해 주세요", gu_list)
    
    filtered = df[df[gu_col] == selected_gu]
    
    if not filtered.empty:
        row = filtered.iloc[0]
        col1, col2, col3 = st.columns(3)
        
        with col1:
            day = row.get("생활쓰레기배출요일", row.get("생활폐기물배출요일", ""))
            render_card("생활쓰레기", "🛍️", day, row, "생활")
        with col2:
            day = row.get("음식물쓰레기배출요일", row.get("음식물폐기물배출요일", ""))
            render_card("음식물", "🍎", day, row, "음식물")
        with col3:
            day = row.get("재활용품배출요일", "")
            render_card("재활용품", "♻️", day, row, "재활용품")

    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.error("파일을 읽을 수 없습니다.")
