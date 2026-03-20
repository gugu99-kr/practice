import re

DAY_ORDER = ["월", "화", "수", "목", "금", "토", "일"]

def normalize_day_text(text):
    """요일 문자열 정리: 중복 제거 + 월~일 순서 정렬"""
    if pd.isna(text):
        return "정보 없음"

    s = str(text).strip()
    if not s:
        return "정보 없음"

    # 구분자 통일
    s = s.replace(" ", "")
    tokens = re.split(r"[+,/·ㆍ\s]+", s)
    tokens = [t for t in tokens if t]

    # 요일만 추출
    found = []
    for day in DAY_ORDER:
        if day in tokens or day in s:
            found.append(day)

    if found:
        return " · ".join(found)

    return s


def normalize_time_text(start, end):
    """시간 문자열 정리"""
    start = safe_text(start)
    end = safe_text(end)

    if start == "정보 없음" and end == "정보 없음":
        return "정보 없음"
    if start != "정보 없음" and end != "정보 없음":
        return f"{start} ~ {end}"
    return start if start != "정보 없음" else end


def pretty_text(text):
    """출력용 텍스트 정리"""
    text = safe_text(text)
    if text == "정보 없음":
        return text
    return text.replace("+", " · ")
