import streamlit as st
import pandas as pd

# 1. 頁面風格設定 (仿 atmarketing 專業配色)
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    /* 整體背景改為極淺灰 */
    .stApp {
        background-color: #f8f9fa;
    }
    /* 卡片樣式：白底、細邊框、柔和陰影 */
    .news-card {
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 10px;
        border: 1px solid #ececec; 
        margin-bottom: 20px; 
        box-shadow: 0 2px 15px rgba(0,0,0,0.03);
        transition: transform 0.2s;
    }
    .news-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    /* 標題顏色：深藍灰色 */
    .main-title {
        text-align: center; 
        color: #2c3e50; 
        font-weight: 800;
        margin-bottom: 30px;
        font-family: "Microsoft JhengHei", sans-serif;
    }
    .rank-tag { 
        color: #5d6d7e; 
        font-weight: bold; 
        font-size: 0.85em; 
        letter-spacing: 1px;
        margin-bottom: 8px; 
        text-transform: uppercase;
    }
    .hot-badge { 
        background-color: #eaf2f8; 
        color: #2980b9; 
        padding: 4px 12px; 
        border-radius: 20px; 
        font-size: 0.8em; 
        font-weight: 600;
    }
    /* 新聞連結顏色 */
    a { 
        text-decoration: none !important; 
        color: #2c3e50 !important; 
    }
    a:hover { 
        color: #3498db !important; 
    }
    h3 {
        margin-top: 5px !important;
        line-height: 1.4;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>📡 資策會輿情熱度觀測站</h1>", unsafe_allow_html=True)

# 2. 數據處理 (維持自動感應邏輯)
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(csv_url)
    
    if df.empty:
        st.warning("⚠️ 試算表中目前沒有資料，請執行 n8n 流程。")
    else:
        # 自動偵測連結與標題欄位
        col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), df.columns[-1])
        col_title = next((c for c in df.columns if '標題' in c or 'Title' in c), None)
        if not col_title:
            col_title = df.drop(columns=[col_link]).apply(lambda x: x.astype(str).str.len().mean()).idxmax()

        # 統計熱度
        hot_counts = df[col_title].value_counts().reset_index()
        hot_counts.columns = [col_title, 'count']

        st.info(f"💡 目前已分析 {len(df)} 筆輿情數據，以下為熱門排行：")

        # 3. 顯示卡片清單
        for i, (_, row) in enumerate(hot_counts.head(15).iterrows()):
            title = row[col_title]
            count = row['count']
            link = df[df[col_title] == title][col_link].values[0]
            
            # 獎牌圖示
            medal = "🥇 " if i == 0 else "🥈 " if i == 1 else "🥉 " if i == 2 else f"#{i+1} "
            
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-tag">{medal} TRENDING TOPICS</div>
                    <a href="{link}" target="_blank"><h3>{title}</h3></a>
                    <div style="margin-top: 10px;">
                        <span class="hot-badge">📊 媒體露出：{count} 次</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ 讀取發生錯誤。錯誤訊息: {e}")
