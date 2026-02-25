import streamlit as st
import pandas as pd
from urllib.parse import urlparse

# 1. 頁面風格設定
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e0e0e; color: #f0f0f0; }
    .news-card {
        background-color: #1a1a1a; padding: 30px; border-radius: 15px;
        border: 1px solid #333333; margin-bottom: 25px; 
    }
    .main-title { text-align: center; color: #ffffff; font-weight: 900; font-size: 2.5em; margin-bottom: 5px; }
    .sub-title { text-align: center; color: #d4af37; font-size: 1.1em; font-weight: 500; margin-bottom: 50px; letter-spacing: 3px; }
    
    .rank-tag { color: #d4af37; font-weight: 900; margin-bottom: 12px; display: flex; align-items: center; gap: 10px; }
    .top-1 { font-size: 2.2em; color: #ffd700; }
    .top-2 { font-size: 1.9em; color: #c0c0c0; }
    .top-3 { font-size: 1.7em; color: #cd7f32; }
    
    .source-container { margin-top: 20px; padding-top: 15px; border-top: 1px dashed #444; }
    .source-title { color: #888; font-size: 0.85em; margin-bottom: 10px; font-weight: bold; }
    
    /* 媒體標籤樣式 */
    .source-link {
        display: inline-block;
        background-color: #2c2c2c;
        color: #d4af37 !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8em;
        margin-right: 10px;
        margin-bottom: 10px;
        border: 1px solid #d4af37;
        text-decoration: none;
        transition: all 0.3s;
    }
    .source-link:hover { background-color: #d4af37; color: #000 !important; }
    
    h3 { font-size: 1.5em !important; line-height: 1.4; margin: 10px 0 !important; font-weight: 700; color: #fff; }
    </style>
    """, unsafe_allow_html=True)

# 媒體名稱轉換表 (可自行擴充)
MEDIA_MAP = {
    "yahoo.com": "Yahoo新聞",
    "udn.com": "聯合新聞網",
    "ltn.com.tw": "自由時報",
    "chinatimes.com": "中時新聞網",
    "ettoday.net": "ETtoday",
    "storm.mg": "風傳媒",
    "cna.com.tw": "中央社",
    "setn.com": "三立新聞",
    "tvbs.com.tw": "TVBS",
    "mirrormedia.mg": "鏡週刊",
    "find.org.tw": "FIND中心",
    "iii.org.tw": "資策會官網"
}

def get_media_name(url):
    domain = urlparse(url).netloc
    for key, name in MEDIA_MAP.items():
        if key in domain:
            return name
    return domain.replace("www.", "")

st.markdown("<h1 class='main-title'>📡 資策會輿情熱度觀測站</h1>")
st.markdown("<p class='sub-title'>WEEKLY TRENDING REPORT</p>")

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 💡 修正標題跑掉：使用更嚴謹的讀取方式
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python')
    
    if df.empty:
        st.warning("⚠️ 試算表中目前沒有資料。")
    else:
        # 鎖定欄位：第3欄是標題，第4欄是連結
        col_title = df.columns[2]
        col_link = df.columns[3]
        
        # 移除標題中的多餘空白與特殊換行
        df[col_title] = df[col_title].astype(str).str.strip().replace(r'\n', '', regex=True)

        # 分組聚合
        grouped = df.groupby(col_title)[col_link].apply(list).reset_index()
        grouped['count'] = grouped[col_link].apply(len)
        grouped = grouped.sort_values(by='count', ascending=False).head(15)

        for i, (_, row) in enumerate(grouped.iterrows()):
            title = row[col_title]
            links = row[col_link]
            count = row['count']
            
            # 排名 HTML
            if i == 0: rank_html = f'<div class="rank-tag top-1">🥇 CHAMPION</div>'
            elif i == 1: rank_html = f'<div class="rank-tag top-2">🥈 SILVER</div>'
            elif i == 2: rank_html = f'<div class="rank-tag top-3">🥉 BRONZE</div>'
            else: rank_html = f'<div class="rank-tag" style="font-size:1.2em; color:#888;">TOP {i+1}</div>'
            
            # 生成媒體標籤 HTML
            links_html = ""
            seen_media = set()
            for url in links:
                m_name = get_media_name(url)
                # 避免同個媒體在同一張卡片重複出現
                links_html += f'<a class="source-link" href="{url}" target="_blank">🌐 {m_name}</a>'
            
            st.markdown(f"""
                <div class="news-card">
                    {rank_html}
                    <h3>{title}</h3>
                    <div style="color: #ffd700; font-weight: bold; font-size: 0.9em; margin-bottom: 10px;">
                        🔥 本週熱度：{count} 次報導
                    </div>
                    <div class="source-container">
                        <div class="source-title">🔗 媒體來源清單：</div>
                        {links_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ 系統校準中，請稍候。錯誤: {e}")
