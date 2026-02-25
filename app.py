import streamlit as st
import pandas as pd

# 1. 頁面風格設定 (加強版深色大賞風格)
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    /* 整體背景：深黑色 */
    .stApp {
        background-color: #0e0e0e;
        color: #f0f0f0;
    }
    /* 卡片樣式：加大邊距與圓角 */
    .news-card {
        background-color: #1a1a1a; 
        padding: 30px; 
        border-radius: 15px;
        border: 1px solid #333333; 
        margin-bottom: 25px; 
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .news-card:hover {
        transform: scale(1.02);
        border-color: #d4af37;
        box-shadow: 0 15px 30px rgba(212, 175, 55, 0.15);
    }
    /* 標題設定 */
    .main-title {
        text-align: center; 
        color: #ffffff; 
        font-weight: 900;
        font-size: 2.5em;
        margin-bottom: 5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .sub-title {
        text-align: center;
        color: #d4af37; /* 金色副標 */
        font-size: 1.1em;
        font-weight: 500;
        margin-bottom: 50px;
        letter-spacing: 3px;
    }
    /* 🏆 排名與獎盃：特大號設定 */
    .rank-tag { 
        color: #d4af37; 
        font-weight: 900; 
        font-size: 1.6em; /* 放大字體 */
        margin-bottom: 12px; 
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .top-1 { color: #ffd700; font-size: 2.2em; } /* 第一名特別大 */
    .top-2 { color: #c0c0c0; font-size: 1.9em; }
    .top-3 { color: #cd7f32; font-size: 1.7em; }
    
    /* 熱度標籤 */
    .hot-badge { 
        background-color: rgba(212, 175, 55, 0.1); 
        color: #d4af37; 
        padding: 6px 18px; 
        border-radius: 50px; 
        font-size: 0.9em; 
        font-weight: 700;
        border: 1px solid rgba(212, 175, 55, 0.3);
        margin-top: 15px;
        display: inline-block;
    }
    /* 連結與標題 */
    a { text-decoration: none !important; color: #ffffff !important; }
    a:hover { color: #d4af37 !important; }
    h3 {
        font-size: 1.5em !important;
        line-height: 1.4;
        margin: 10px 0 !important;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>📡 資策會輿情熱度觀測站</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>WEEKLY TRENDING REPORT</p>", unsafe_allow_html=True)

# 2. 數據處理
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(csv_url)
    
    if df.empty:
        st.warning("⚠️ 試算表中目前沒有資料，請執行 n8n 流程。")
    else:
        col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), df.columns[-1])
        col_title = next((c for c in df.columns if '標題' in c or 'Title' in c), None)
        if not col_title:
            col_title = df.drop(columns=[col_link]).apply(lambda x: x.astype(str).str.len().mean()).idxmax()

        hot_counts = df[col_title].value_counts().reset_index()
        hot_counts.columns = [col_title, 'count']

        # 3. 顯示卡片清單
        for i, (_, row) in enumerate(hot_counts.head(15).iterrows()):
            title = row[col_title]
            count = row['count']
            link = df[df[col_title] == title][col_link].values[0]
            
            # 根據排名給予不同樣式與圖示
            if i == 0:
                rank_html = f'<div class="rank-tag top-1">🥇 CHAMPION</div>'
            elif i == 1:
                rank_html = f'<div class="rank-tag top-2">🥈 SILVER</div>'
            elif i == 2:
                rank_html = f'<div class="rank-tag top-3">🥉 BRONZE</div>'
            else:
                rank_html = f'<div class="rank-tag" style="font-size:1.2em; color:#888;">TOP {i+1}</div>'
            
            st.markdown(f"""
                <div class="news-card">
                    {rank_html}
                    <a href="{link}" target="_blank"><h3>{title}</h3></a>
                    <div class="hot-badge">🔥 熱度權重：{count * 10} pts — 報導次數 {count}</div>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ 讀取發生錯誤。錯誤訊息: {e}")
