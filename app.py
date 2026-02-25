import streamlit as st
import pandas as pd

# 1. 頁面風格設定
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e0e0e; color: #f0f0f0; }
    .news-card {
        background-color: #1a1a1a; 
        padding: 30px; 
        border-radius: 15px;
        border: 1px solid #333333; 
        margin-bottom: 25px; 
    }
    .main-title { text-align: center; color: #ffffff; font-weight: 900; font-size: 2.5em; margin-bottom: 5px; }
    .sub-title { text-align: center; color: #d4af37; font-size: 1.1em; font-weight: 500; margin-bottom: 50px; letter-spacing: 3px; }
    
    /* 排名標籤 */
    .rank-tag { color: #d4af37; font-weight: 900; margin-bottom: 12px; display: flex; align-items: center; gap: 10px; }
    .top-1 { font-size: 2.2em; color: #ffd700; }
    .top-2 { font-size: 1.9em; color: #c0c0c0; }
    .top-3 { font-size: 1.7em; color: #cd7f32; }
    
    /* 媒體連結清單樣式 */
    .source-container {
        margin-top: 20px;
        padding-top: 15px;
        border-top: 1px dashed #444;
    }
    .source-title {
        color: #888;
        font-size: 0.85em;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .source-link {
        display: inline-block;
        background-color: #2c2c2c;
        color: #d4af37 !important;
        padding: 5px 12px;
        border-radius: 4px;
        font-size: 0.8em;
        margin-right: 8px;
        margin-bottom: 8px;
        border: 1px solid #444;
        transition: all 0.2s;
    }
    .source-link:hover {
        background-color: #d4af37;
        color: #000 !important;
    }
    h3 { font-size: 1.5em !important; line-height: 1.4; margin: 10px 0 !important; font-weight: 700; color: #fff; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>📡 資策會輿情熱度觀測站</h1>")
st.markdown("<p class='sub-title'>WEEKLY TRENDING REPORT</p>")

# 2. 數據處理
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(csv_url)
    
    if df.empty:
        st.warning("⚠️ 試算表中目前沒有資料。")
    else:
        # 自動偵測欄位
        col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), df.columns[-1])
        col_title = next((c for c in df.columns if '標題' in c or 'Title' in c), None)
        if not col_title:
            col_title = df.drop(columns=[col_link]).apply(lambda x: x.astype(str).str.len().mean()).idxmax()

        # --- 核心邏輯：根據標題分組並收集所有連結 ---
        # 統計次數並保留連結清單
        grouped = df.groupby(col_title)[col_link].apply(list).reset_index()
        grouped['count'] = grouped[col_link].apply(len)
        # 排序：從次數多到少
        grouped = grouped.sort_values(by='count', ascending=False).head(15)

        # 3. 顯示卡片清單
        for i, (_, row) in enumerate(grouped.iterrows()):
            title = row[col_title]
            links = row[col_link]
            count = row['count']
            
            # 設定排名樣式
            if i == 0: rank_html = f'<div class="rank-tag top-1">🥇 CHAMPION</div>'
            elif i == 1: rank_html = f'<div class="rank-tag top-2">🥈 SILVER</div>'
            elif i == 2: rank_html = f'<div class="rank-tag top-3">🥉 BRONZE</div>'
            else: rank_html = f'<div class="rank-tag" style="font-size:1.2em; color:#888;">TOP {i+1}</div>'
            
            # 生成媒體連結按鈕 HTML
            links_html = "".join([f'<a class="source-link" href="{url}" target="_blank">來源 {idx+1}</a>' for idx, url in enumerate(links)])
            
            st.markdown(f"""
                <div class="news-card">
                    {rank_html}
                    <h3>{title}</h3>
                    <div style="color: #ffd700; font-weight: bold; font-size: 0.9em; margin-bottom: 10px;">
                        🔥 本週熱度：{count} 次報導
                    </div>
                    <div class="source-container">
                        <div class="source-title">🔗 查看原始報導連結：</div>
                        {links_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ 讀取發生錯誤：{e}")
