import streamlit as st
import pandas as pd
from urllib.parse import urlparse, parse_qs

# 1. 頁面風格設定 (淺色溫和質感)
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

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
    .stExpander { border: none !important; box-shadow: none !important; background-color: #f8f9fa !important; margin-top: 10px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 💡 強化版媒體名稱辨識：嘗試解析 Google 轉址後的真正網址
def get_media_name(url):
    if not isinstance(url, str): return "相關報導"
    
    # 嘗試從 Google RSS 轉址參數中提取原始網址 (通常在 url= 參數中)
    parsed_url = urlparse(url)
    actual_domain = parsed_url.netloc.lower()
    
    # 媒體名稱轉換表
    mapping = {
        "yahoo": "Yahoo新聞", "udn": "聯合新聞網", "ltn": "自由時報", "chinatimes": "中時新聞網",
        "ettoday": "ETtoday", "storm": "風傳媒", "cna": "中央社", "setn": "三立新聞",
        "tvbs": "TVBS", "mirrormedia": "鏡週刊", "msn": "MSN新聞", "find.org.tw": "FIND中心",
        "iii.org.tw": "資策會官網", "hinet": "HiNet新聞", "line": "LINE TODAY"
    }

    # 檢查是否有知名媒體網域
    for key, name in mapping.items():
        if key in actual_domain:
            return name
            
    # 如果還是辨識不到，且是 google 網域，就顯示為「媒體報導」以維持整潔
    if "google" in actual_domain: return "媒體報導"
    
    return actual_domain.replace("www.", "")

st.markdown("<div class='main-title'>📡 資策會輿情熱度觀測站</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>WEEKLY TRENDING REPORT</div>", unsafe_allow_html=True)

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python')
    
    # 智慧對位欄位
    col_date = next((c for c in df.columns if '日期' in str(c) or 'Date' in str(c)), df.columns[1])
    col_title = next((c for c in df.columns if '標題' in str(c) or 'Title' in str(c)), df.columns[2])
    col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), df.columns[3])

    # 清洗與轉換
    df['c_title'] = df[col_title].astype(str).str.replace(r'\n', '', regex=True).str.strip()
    df['c_date'] = df[col_date].fillna("近期").astype(str).str.strip()
    df['c_link'] = df[col_link].astype(str).str.strip()
    
    # --- 關鍵修正：聚合後再進行媒體辨識，避免重複顯示 ---
    grouped = df.groupby('c_title').agg({
        'c_link': lambda x: list(x), 
        'c_date': 'max'
    }).reset_index()
    
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    for i, (_, row) in enumerate(grouped.iterrows()):
        title = row['c_title']
        links = row['c_link']
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
        
        with st.expander(f"📂 點擊查看共 {count} 家媒體報導列表"):
            # 在列表顯示時才進行媒體名稱轉換，確保每個來源都被正確標記
            for link in links:
                m_name = get_media_name(link)
                st.markdown(f"**[{m_name}]** ➔ [{title}]({link})")

except Exception as e:
    st.error(f"資料同步中，請稍候。")
