import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote_plus
from datetime import datetime, timedelta, date

# ✅ 페이지 설정 + favicon
st.set_page_config(
    page_title="뉴스 북마크",
    page_icon="📰",
    layout="centered"
)

# ✅ 날짜 포맷 변환
def format_korean_date(pub_date_str: str):
    try:
        dt = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")
        return dt, f"{dt.year}년 {dt.month}월 {dt.day}일 {dt.hour:02d}:{dt.minute:02d}분"
    except Exception:
        return None, pub_date_str

# ✅ 구글 뉴스 RSS 수집
def get_news_from_google(keyword: str, max_entries: int = 10):
    encoded_keyword = quote_plus(keyword)
    url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)

    results = []
    for entry in feed.entries[:max_entries]:
        dt_obj, pretty = format_korean_date(entry.published)
        source = entry.title.split(" - ")[-1] if " - " in entry.title else ""
        results.append(
            {
                "키워드": keyword,
                "제목": entry.title,
                "링크": entry.link,
                "날짜": pretty,
                "날짜객체": dt_obj,
                "출처": source,
            }
        )
    return results

# ✅ 키워드별 색상
def assign_color_palette(keywords):
    palette = [
        "#f94144", "#f3722c", "#f9c74f", "#90be6d",
        "#43aa8b", "#577590", "#277da1"
    ]
    return {kw: palette[i % len(palette)] for i, kw in enumerate(keywords)}

# ──────────────────────────────────────────────────────────
def main():
    st.title("📰 키워드 뉴스 북마크")
    st.caption("키워드를 선택하고, 기간을 지정해 관련 뉴스를 한눈에 모아보세요.")

    # 세션 상태 초기화
    if "all_keywords" not in st.session_state:
        st.session_state.all_keywords = ["2026학년도 대입", "논술", "수능", "수시"]
    if "selected_keywords" not in st.session_state:
        st.session_state.selected_keywords = st.session_state.all_keywords.copy()

    # ➕ 키워드 추가
    st.markdown("### ➕ 키워드 추가")
    c1, c2 = st.columns([3, 2])
    with c1:
        new_kw_input = st.text_input("쉼표로 구분된 키워드", placeholder="예: 고교학점제, 정시 확대")
    with c2:
        st.write("")
        if st.button("✅ 추가", use_container_width=True):
            for kw in [k.strip() for k in new_kw_input.split(",") if k.strip()]:
                if kw not in st.session_state.all_keywords:
                    st.session_state.all_keywords.append(kw)
                    st.session_state.selected_keywords.append(kw)
            st.rerun()

    # 🎯 키워드 선택
    st.markdown("### 🎯 검색할 키워드 선택")
    selected = st.multiselect(
        "현재 사용할 키워드를 선택하세요",
        st.session_state.all_keywords,
        default=st.session_state.selected_keywords,
    )
    st.session_state.selected_keywords = selected

    # 📆 기간 설정
    st.markdown("### 📆 검색 기간 설정")
    today = date.today()
    default_start = today - timedelta(days=7)
    date_sel = st.date_input(
        "기간 (시작일 또는 시작·종료일)",
        value=(default_start, today),
        help="하나만 찍으면 해당 날짜 이후, 두 개 찍으면 범위로 필터링",
    )
    # date_input 반환값 표준화
    if isinstance(date_sel, tuple):
        date_start = date_sel[0]
        date_end = date_sel[1] if len(date_sel) > 1 else today
    else:
        date_start, date_end = date_sel, today

    # 🔘 정렬 방식
    sort_by = st.radio("정렬 기준", ["키워드순", "날짜순"], horizontal=True)

    st.divider()

    # 뉴스 수집 및 기간 필터
    news_all = []
    for kw in st.session_state.selected_keywords:
        news_all.extend(get_news_from_google(kw))

    news_filtered = [
        n for n in news_all
        if n["날짜객체"] and date_start <= n["날짜객체"].date() <= date_end
    ]

    # 정렬
    if sort_by == "날짜순":
        news_filtered.sort(key=lambda x: x["날짜객체"], reverse=True)
    else:
        news_filtered.sort(key=lambda x: (x["키워드"], x["날짜객체"] or datetime.min))

    # 색상 매핑
    color_map = assign_color_palette(st.session_state.selected_keywords)

    # 🗞 출력
    st.markdown("### 🗞 뉴스 목록")
    if news_filtered:
        for item in news_filtered:
            color = color_map.get(item["키워드"], "#888888")
            st.markdown(
                f"""
                <div style='margin-bottom:8px;'>
                  <span style='background-color:{color}; color:#fff; padding:2px 8px;
                       border-radius:10px; font-size:13px; font-weight:600;'>
                       {item['키워드']}
                  </span>
                  <a href="{item['링크']}" target="_blank"
                     style='margin-left:10px; font-weight:600; color:#1a73e8; text-decoration:none;'>
                     {item['제목']}
                  </a>
                  <span style='color:gray; font-size:12px;'> — {item['날짜']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("해당 기간에 선택한 키워드의 뉴스가 없습니다.")

if __name__ == "__main__":
    main()
