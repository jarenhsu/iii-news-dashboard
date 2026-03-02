import streamlit as st
import pandas as pd
from urllib.parse import urlparse

# 1. 頁面風格設定 (淺色溫和質感)
st.set_page_config(page_title="資策會輿情觀測站", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcf9; color: #37474f; }
    .news-card {
        background-color: #ffffff; padding: 25px; border-radius: 12px;
        border: 1px solid #f0f0ed; margin-bottom: 25px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }
    .main-title { text-align: center; color: #263238; font-weight: 800; font-size: 2.2em; margin-top: 10px; }
    .sub-title { text-align: center; color: #90a4ae; font-size: 1em; margin-bottom: 30px; }
    .rank-text { color: #af946d; font-weight: 900; font-size: 1.5em; margin-bottom: 5px; }
    .topic-title { font-size: 1.4em; font-weight: 700; color: #2c3e50; margin-bottom: 15px; line-height: 1.4; }
    .info-bar { margin-bottom: 15px; font-size: 0.85em; color: #95a5a6; }
    /* 媒體展開樣式 */
    .stExpander { border: none !important; box-shadow: none !important; background-color: #f8f9fa !important; margin-top: 10px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 媒體名稱辨識函數
def get_media_name(url):
    if not isinstance(url, str) or "google" in url: return "網路媒體"
    mapping = {
        "yahoo": "Yahoo新聞", "udn": "聯合新聞", "ltn": "自由時報", "chinatimes": "中時新聞",
        "ettoday": "ETtoday", "storm": "風傳媒", "cna": "中央社", "setn": "三立新聞",
        "tvbs": "TVBS", "find.org.tw": "FIND中心", "iii.org.tw": "資策會官網"
    }
    domain = urlparse(url).netloc.lower()
    for key, name in mapping.items():
        if key in domain: return name
    return domain.split('.')[-2] if '.' in domain else "相關報導"

st.markdown("<div class='main-title'>📡 資策會輿情熱度觀測站</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>媒體露出 > 標題清單分析儀表板</div>", unsafe_allow_html=True)

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python')
    
    # 欄位對位
    col_date = next((c for c in df.columns if '日期' in str(c) or 'Date' in str(c)), df.columns[1])
    col_title = next((c for c in df.columns if '標題' in str(c) or 'Title' in str(c)), df.columns[2])
    col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), df.columns[3])

    df['c_title'] = df[col_title].astype(str).str.replace(r'\n', '', regex=True).str.strip()
    df['c_date'] = df[col_date].fillna("近期").astype(str).str.strip()
    df['c_link'] = df[col_link].astype(str).str.strip()
    df['media'] = df['c_link'].apply(get_media_name)

    # 聚合：以標題分組，收集日期、媒體與連結
    grouped = df.groupby('c_title').agg({
        'c_link': list, 
        'media': list, 
        'c_date': 'max'
    }).reset_index()
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    for i, (_, row) in enumerate(grouped.iterrows()):
        title = row['c_title']
        links = row['c_link']
        medias = row['media']
        latest_date = row['c_date']
        count = row['count']
        
        medal = "🥇 CHAMPION" if i == 0 else "🥈 SILVER" if i == 1 else "🥉 BRONZE" if i == 2 else f"TOP {i+1}"
        
        st.markdown(f"""
            <div class="news-card">
                <div class="rank-text">{medal}</div>
                <div class="topic-title">{title}</div>
                <div class="info-bar">📅 最新日期：{latest_date} ｜ 🔥 本週累計：{count} 次媒體露出</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 建立媒體 > 標題列表 (使用 Expander)
        with st.expander(f"📂 點擊查看共 {count} 家媒體報導列表"):
            for link, m_name in zip(links, medias):
                st.markdown(f"**[{m_name}]** ➔ [{title}]({link})")

except Exception as e:
    st.error("系統資料同步中，請確認試算表格式。")
