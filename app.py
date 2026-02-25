import streamlit as st
import pandas as pd
from urllib.parse import urlparse

# 1. 頁面風格設定
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e0e0e; color: #f0f0f0; }
    .news-card {
        background-color: #1a1a1a; padding: 35px; border-radius: 15px;
        border: 1px solid #333333; margin-bottom: 25px; 
    }
    .main-title { text-align: center; color: #ffffff; font-weight: 900; font-size: 2.2em; margin-bottom: 5px; }
    .sub-title { text-align: center; color: #d4af37; font-size: 1em; font-weight: 500; margin-bottom: 40px; letter-spacing: 3px; }
    .rank-tag { color: #d4af37; font-weight: 900; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
    .top-1 { font-size: 2.2em; color: #ffd700; }
    .top-2 { font-size: 1.8em; color: #c0c0c0; }
    .top-3 { font-size: 1.6em; color: #cd7f32; }
    .source-container { margin-top: 25px; padding-top: 20px; border-top: 1px dashed #444; }
    .source-title { color: #888; font-size: 0.85em; margin-bottom: 12px; font-weight: bold; }
    .source-link {
        display: inline-block; background-color: #2c2c2c; color: #d4af37 !important;
        padding: 8px 16px; border-radius: 25px; font-size: 0.85em;
        margin-right: 10px; margin-bottom: 10px; border: 1px solid #d4af37;
        text-decoration: none; transition: all 0.3s;
    }
    .source-link:hover { background-color: #d4af37; color: #000 !important; }
    h3 { font-size: 1.6em !important; line-height: 1.4; margin: 15px 0 !important; font-weight: 700; color: #fff; }
    </style>
    """, unsafe_allow_html=True)

# 媒體名稱轉換加強版 (針對 Google RSS 優化)
def get_media_name(url):
    if not isinstance(url, str): return "新聞來源"
    # 如果是 Google 轉址，試著從後方參數抓取，若抓不到則顯示通用標籤
    domain = urlparse(url).netloc.lower()
    if "google" in domain: return "媒體報導" 
    
    mapping = {
        "yahoo": "Yahoo新聞", "udn": "聯合新聞網", "ltn": "自由時報", "chinatimes": "中時",
        "ettoday": "ETtoday", "storm": "風傳媒", "cna": "中央社", "setn": "三立新聞",
        "tvbs": "TVBS", "mirrormedia": "鏡週刊", "find.org.tw": "FIND中心", "iii.org.tw": "資策會官網"
    }
    for key, name in mapping.items():
        if key in domain: return name
    return domain.split('.')[-2] if '.' in domain else "新聞媒體"

st.markdown("<h1 class='main-title'>📡 資策會輿情熱度觀測站</h1>")
st.markdown("<p class='sub-title'>WEEKLY TRENDING REPORT</p>")

# 2. 數據處理 (指向你的新 ID)
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 💡 修正標題讀取：強制跳過損壞行，並清理不必要的空白
    df = pd.read_csv(csv_url, on_bad_lines='skip')
    df = df.dropna(subset=[df.columns[2], df.columns[3]]) # 確保標題與連結都在

    if not df.empty:
        # 鎖定：第3欄(索引2)為標題，第4欄(索引3)為連結
        df['clean_title'] = df.iloc[:, 2].astype(str).str.strip()
        df['clean_link'] = df.iloc[:, 3].astype(str).str.strip()
        
        # 聚合資料
        grouped = df.groupby('clean_title')['clean_link'].apply(list).reset_index()
        grouped['count'] = grouped['clean_link'].apply(len)
        grouped = grouped.sort_values(by='count', ascending=False).head(15)

        for i, (_, row) in enumerate(grouped.iterrows()):
            title = row['clean_title']
            links = row['clean_link']
            count = row['count']
            
            # 排名設計
            if i == 0: rank_html = '<div class="rank-tag top-1">🥇 CHAMPION</div>'
            elif i == 1: rank_html = '<div class="rank-tag top-2">🥈 SILVER</div>'
            elif i == 2: rank_html = '<div class="rank-tag top-3">🥉 BRONZE</div>'
            else: rank_html = f'<div class="rank-tag" style="font-size:1.2em; color:#888;">TOP {i+1}</div>'
            
            # 生成來源標籤
            links_html = "".join([f'<a class="source-link" href="{url}" target="_blank">🌐 {get_media_name(url)}</a>' for url in links if url])
            
            st.markdown(f"""
                <div class="news-card">
                    {rank_html}
                    <h3>{title}</h3>
                    <div style="color: #ffd700; font-weight: bold; font-size: 1em; margin-bottom: 10px;">
                        🔥 本週熱度：{count} 次媒體報導
                    </div>
                    <div class="source-container">
                        <div class="source-title">🔗 參與報導媒體：</div>
                        {links_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
except Exception as e:
    st.error(f"系統自動更新中，請稍候。")
