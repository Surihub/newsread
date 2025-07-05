import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote_plus
from datetime import datetime

def get_news_from_google(keyword, max_entries=10):
    encoded_keyword = quote_plus(keyword)
    feed_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(feed_url)
    results = []
    for entry in feed.entries[:max_entries]:
        results.append({
            "키워드": keyword,
            "제목": entry.title,
            "링크": entry.link,
            "날짜": entry.published
        })
    return results

def main():
    st.set_page_config(page_title="뉴스 북마크", layout="wide")
    st.title("📰 키워드 뉴스 북마크")
    st.caption("키워드를 선택하고, 실시간으로 관련 뉴스를 모아보세요.")

    # 1. 세션 상태 초기화
    if "all_keywords" not in st.session_state:
        st.session_state.all_keywords = ["2026학년도 대입", "논술", "수능", "수시"]

    # 2. 키워드 추가 UI
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

    # 3. 키워드 선택 멀티셀렉트
    st.markdown("### 🎯 검색할 키워드 선택")
    selected_keywords = st.multiselect(
        label="현재 사용할 키워드를 선택하세요",
        options=st.session_state.all_keywords,
        default=st.session_state.all_keywords
    )

    st.divider()

    # 4. 뉴스 크롤링 및 출력
    all_news = []
    for kw in selected_keywords:
        with st.expander(f"📌 {kw} 관련 뉴스"):
            news = get_news_from_google(kw)
            if news:
                for item in news:
                    st.markdown(
                        f"""<div style='margin-bottom:10px;'>
                        <a href="{item['링크']}" target="_blank" style='text-decoration:none; color:#1a73e8; font-weight:bold;'>{item['제목']}</a>
                        <div style='color:gray; font-size:12px;'>{item['날짜']}</div>
                        </div>""",
                        unsafe_allow_html=True
                    )
                all_news.extend(news)
            else:
                st.info("🔎 관련 뉴스가 없습니다.")

    # 5. 다운로드
    if all_news:
        df = pd.DataFrame(all_news)
        csv_data = df.to_csv(index=False, encoding="euc-kr")
        now_str = datetime.now().strftime("%Y%m%d_%H%M")
        file_name = f"뉴스_북마크_{now_str}.csv"

        st.markdown("---")
        st.markdown("### 📥 뉴스 목록 저장")
        st.download_button("⬇️ CSV 다운로드", data=csv_data, file_name=file_name)

if __name__ == "__main__":
    main()
