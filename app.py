import streamlit as st
import pandas as pd

# 1. 頁面風格設定 (深色大賞 + 來源編號)
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e0e0e; color: #f0f0f0; }
    .news-card {
        background-color: #1a1a1a; padding: 35px; border-radius: 15px;
        border: 1px solid #333; margin-bottom: 25px; 
    }
    .main-title { text-align: center; color: #fff; font-weight: 900; font-size: 2.2em; margin-top: 20px; }
    .sub-title { text-align: center; color: #d4af37; font-size: 1em; margin-bottom: 40px; letter-spacing: 2px; }
    .rank-text { color: #d4af37; font-weight: 900; font-size: 1.8em; margin-bottom: 10px; }
    .news-title { font-size: 1.5em; font-weight: 700; color: #fff; margin: 10px 0; line-height: 1.4; }
    .source-container { margin-top: 20px; padding-top: 15px; border-top: 1px dashed #444; }
    .source-btn {
        display: inline-block; background-color: #2c2c2c; color: #d4af37 !important;
        padding: 6px 16px; border-radius: 5px; font-size: 0.85em;
        margin: 5px; border: 1px solid #333; text-decoration: none; transition: 0.3s;
    }
    .source-btn:hover { background-color: #d4af37; color: #000 !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-title'>📡 資策會輿情熱度觀測站</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>WEEKLY TRENDING REPORT</div>", unsafe_allow_html=True)

# 2. 數據處理
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 💡 讀取並強制清理資料格式
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python')
    
    # 💡 鎖定：第3欄標題，第4欄連結
    df['title'] = df.iloc[:, 2].astype(str).str.replace(r'\n', '', regex=True).str.strip()
    df['link'] = df.iloc[:, 3].astype(str).str.strip()

    # 排除無效資料與標頭
    df = df[df['title'].str.len() > 2] # 標題太短的通常是雜訊
    df = df[~df['title'].str.contains("新聞標題")]

    # 聚合資料
    grouped = df.groupby('title')['link'].apply(list).reset_index()
    grouped['count'] = grouped['link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(20) # 顯示前 20 名

    if grouped.empty:
        st.info("💡 目前資料同步中，請確保試算表已有寫入內容。")
    else:
        for i, (_, row) in enumerate(grouped.iterrows()):
            title = row['title']
            links = row['link']
            count = row['count']
            
            # 設定獎牌顏色
            if i == 0:
                medal_html = '<div class="rank-text" style="color:#ffd700;">🥇 CHAMPION</div>'
            elif i == 1:
                medal_html = '<div class="rank-text" style="color:#c0c0c0;">🥈 SILVER</div>'
            elif i == 2:
                medal_html = '<div class="rank-text" style="color:#cd7f32;">🥉 BRONZE</div>'
            else:
                medal_html = f'<div class="rank-text" style="color:#888;">TOP {i+1}</div>'
            
            # 生成來源按鈕
            links_html = "".join([f'<a class="source-btn" href="{u}" target="_blank">來源 {idx+1}</a>' for idx, u in enumerate(links) if 'http' in str(u)])
            
            st.markdown(f"""
                <div class="news-card">
                    {medal_html}
                    <div class="news-title">{title}</div>
                    <div style="color: #d4af37; font-weight: bold; margin-bottom: 10px;">🔥 熱度：{count} 次報導</div>
                    <div class="source-container">
                        <div style="color: #666; font-size: 0.8em; margin-bottom: 10px;">🔗 原始報導連結：</div>
                        {links_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"系統自動校準中，請稍候重新整理。")
