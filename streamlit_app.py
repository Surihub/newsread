import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote_plus
from datetime import datetime

def format_korean_date(pub_date_str):
    try:
        dt = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")
        return dt, f"{dt.year}년 {dt.month}월 {dt.day}일 {dt.hour:02d}:{dt.minute:02d}분"
    except:
        return None, pub_date_str

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

def assign_color_palette(keywords):
    palette = ["#f94144", "#f3722c", "#f9c74f", "#90be6d", "#43aa8b", "#577590", "#277da1"]
    return {kw: palette[i % len(palette)] for i, kw in enumerate(keywords)}

def main():
    st.set_page_config(page_title="뉴스 북마크", layout="wide")
    st.title("📰 키워드 뉴스 북마크")
    st.caption("키워드를 선택하고, 실시간으로 관련 뉴스를 한눈에 모아보세요.")

    # 세션 상태 초기화
    if "all_keywords" not in st.session_state:
        st.session_state.all_keywords = ["2026학년도 대입", "논술", "수능", "수시"]

    # 키워드 추가
    st.markdown("### ➕ 키워드 추가")
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("쉼표로 구분된 키워드 입력", placeholder="예: 고교학점제, 정시 확대")
    with col2:
        st.write("")
        if st.button("✅ 추가"):
            new_keywords = [k.strip() for k in user_input.split(",") if k.strip()]
            for k in new_keywords:
                if k not in st.session_state.all_keywords:
                    st.session_state.all_keywords.append(k)
            st.rerun()

    # 키워드 선택
    st.markdown("### 🎯 검색할 키워드 선택")
    selected_keywords = st.multiselect(
        label="현재 사용할 키워드를 선택하세요",
        options=st.session_state.all_keywords,
        default=st.session_state.all_keywords
    )

    st.divider()

    # 정렬 방식 선택
    sort_by = st.radio("정렬 기준", ["키워드순", "날짜순"], horizontal=True)

    # 뉴스 수집
    all_news = []
    for kw in selected_keywords:
        news = get_news_from_google(kw)
        all_news.extend(news)

    # 정렬 적용
    if sort_by == "날짜순":
        all_news = sorted(
            [n for n in all_news if n["날짜객체"]], 
            key=lambda x: x["날짜객체"], 
            reverse=True
        )
    else:  # 키워드순
        all_news = sorted(all_news, key=lambda x: (x["키워드"], x["날짜객체"] or datetime.min), reverse=False)

    # 키워드 색상 매핑
    color_map = assign_color_palette(selected_keywords)

    # 뉴스 출력
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
