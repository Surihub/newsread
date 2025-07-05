import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote_plus
from datetime import datetime

# ✅ 페이지 설정 + favicon
st.set_page_config(
    page_title="뉴스 북마크",
    page_icon="📰",
    layout="centered"  # 기본값이기도 함

)

# ✅ 날짜 포맷 변환
def format_korean_date(pub_date_str):
    try:
        dt = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")
        return dt, f"{dt.year}년 {dt.month}월 {dt.day}일 {dt.hour:02d}:{dt.minute:02d}분"
    except:
        return None, pub_date_str

# ✅ 구글 뉴스 RSS 수집
def get_news_from_google(keyword, max_entries=10):
    encoded_keyword = quote_plus(keyword)
    feed_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(feed_url)
    results = []
    for entry in feed.entries[:max_entries]:
        dt_obj, formatted_date = format_korean_date(entry.published)
        source = entry.title.split(" - ")[-1] if " - " in entry.title else ""
        results.append({
            "키워드": keyword,
            "제목": entry.title,
            "링크": entry.link,
            "날짜": formatted_date,
            "날짜객체": dt_obj,
            "출처": source
        })
    return results

# ✅ 키워드별 색상 부여
def assign_color_palette(keywords):
    palette = ["#f94144", "#f3722c", "#f9c74f", "#90be6d", "#43aa8b", "#577590", "#277da1"]
    return {kw: palette[i % len(palette)] for i, kw in enumerate(keywords)}

# ✅ 메인 실행
def main():
    st.title("📰 키워드 뉴스 북마크")
    st.caption("키워드를 선택하고, 실시간으로 관련 뉴스를 한눈에 모아보세요.")

    # ✅ 상태 초기화
    if "all_keywords" not in st.session_state:
        st.session_state.all_keywords = ["2026학년도 대입", "논술", "수능", "수시"]

    if "selected_keywords" not in st.session_state:
        st.session_state.selected_keywords = st.session_state.all_keywords.copy()

    # ✅ 키워드 추가
    st.markdown("### ➕ 키워드 추가")
    col1, col2 = st.columns([3, 2])
    with col1:
        user_input = st.text_input("쉼표로 구분된 키워드 입력", placeholder="예: 고교학점제, 정시 확대")
    with col2:
        st.write("")
        if st.button("✅ 추가", use_container_width=True):
            new_keywords = [k.strip() for k in user_input.split(",") if k.strip()]
            for k in new_keywords:
                if k not in st.session_state.all_keywords:
                    st.session_state.all_keywords.append(k)
                    st.session_state.selected_keywords.append(k)
            st.rerun()

    # ✅ 키워드 선택
    st.markdown("### 🎯 검색할 키워드 선택")
    selected = st.multiselect(
        label="현재 사용할 키워드를 선택하세요",
        options=st.session_state.all_keywords,
        default=st.session_state.selected_keywords
    )
    st.session_state.selected_keywords = selected

    st.divider()

    # ✅ 정렬 선택
    sort_by = st.radio("정렬 기준", ["키워드순", "날짜순"], horizontal=True)

    # ✅ 뉴스 수집
    all_news = []
    for kw in st.session_state.selected_keywords:
        all_news.extend(get_news_from_google(kw))

    # ✅ 정렬
    if sort_by == "날짜순":
        all_news = sorted(
            [n for n in all_news if n["날짜객체"]],
            key=lambda x: x["날짜객체"],
            reverse=True
        )
    else:
        all_news = sorted(
            all_news,
            key=lambda x: (x["키워드"], x["날짜객체"] or datetime.min)
        )

    # ✅ 색상 매핑
    color_map = assign_color_palette(st.session_state.selected_keywords)

    # ✅ 뉴스 출력
    if all_news:
        st.markdown("### 🗞 뉴스 목록")
        for item in all_news:
            color = color_map.get(item["키워드"], "#888888")
            st.markdown(
                f"""<div style='margin-bottom:8px;'>
                <span style='background-color:{color}; color:white; padding:3px 8px; border-radius:10px; font-size:13px; font-weight:bold;'>{item["키워드"]}</span>
                <a href="{item['링크']}" target="_blank" style='margin-left:10px; font-weight:600; color:#1a73e8; text-decoration:none;'>{item['제목']}</a>
                <span style='color:gray; font-size:12px;'> — {item['날짜']}</span>
                </div>""",
                unsafe_allow_html=True
            )
    else:
        st.info("선택한 키워드에 대한 뉴스가 없습니다.")

if __name__ == "__main__":
    main()
