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
    .source-link {
        display: inline-block; background-color: #2c2c2c; color: #d4af37 !important;
        padding: 6px 14px; border-radius: 20px; font-size: 0.85em;
        margin-right: 10px; margin-bottom: 10px; border: 1px solid #d4af37;
        text-decoration: none; transition: all 0.3s;
    }
    .source-link:hover { background-color: #d4af37; color: #000 !important; }
    h3 { font-size: 1.5em !important; line-height: 1.4; margin: 10px 0 !important; font-weight: 700; color: #fff; }
    </style>
    """, unsafe_allow_html=True)

# 媒體名稱轉換邏輯
MEDIA_MAP = {
    "yahoo": "Yahoo新聞", "udn": "聯合新聞網", "ltn": "自由時報", "chinatimes": "中時新聞網",
    "ettoday": "ETtoday", "storm": "風傳媒", "cna": "中央社", "setn": "三立新聞",
    "tvbs": "TVBS", "mirrormedia": "鏡週刊", "find.org.tw": "FIND中心", "iii.org.tw": "資策會官網"
}

def get_media_name(url):
    if not isinstance(url, str): return "未知媒體"
    domain = urlparse(url).netloc.lower()
    for key, name in MEDIA_MAP.items():
        if key in domain: return name
    return domain.split('.')[-2] if '.' in domain else domain

st.markdown("<h1 class='main-title'>📡 資策會輿情熱度觀測站</h1>")
st.markdown("<p class='sub-title'>WEEKLY TRENDING REPORT</p>")

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 💡 讀取資料並預防格式錯誤
    df = pd.read_csv(csv_url, on_bad_lines='skip')
    df = df.dropna(how='all') # 刪除全空行

    if not df.empty:
        # 固定使用 C、D 欄位
        col_title = df.columns[2]
        col_link = df.columns[3]
        
        # 清理資料
        df[col_title] = df[col_title].fillna("未知標題").astype(str).str.strip()
        df[col_link] = df[col_link].fillna("")

        # 聚合資料
        grouped = df.groupby(col_title)[col_link].apply(list).reset_index()
        grouped['count'] = grouped[col_link].apply(len)
        grouped = grouped.sort_values(by='count', ascending=False).head(15)

        for i, (_, row) in enumerate(grouped.iterrows()):
            title = row[col_title]
            links = row[col_link]
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
    st.error(f"資料讀取中，請稍候再重新整理。")
