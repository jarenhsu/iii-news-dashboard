import streamlit as st
import pandas as pd

# 1. 頁面風格設定 (仿圭話行銷深色質感)
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    /* 整體背景改為深黑色 */
    .stApp {
        background-color: #121212;
        color: #e0e0e0;
    }
    /* 卡片樣式：深灰底、細邊框、懸浮發光效果 */
    .news-card {
        background-color: #1e1e1e; 
        padding: 25px; 
        border-radius: 12px;
        border: 1px solid #333333; 
        margin-bottom: 20px; 
        transition: all 0.3s ease;
    }
    .news-card:hover {
        transform: translateY(-5px);
        border-color: #d4af37; /* 懸浮時邊框變金黃色 */
        box-shadow: 0 10px 20px rgba(212, 175, 55, 0.1);
    }
    /* 標題顏色：純白 */
    .main-title {
        text-align: center; 
        color: #ffffff; 
        font-weight: 800;
        margin-bottom: 10px;
        letter-spacing: 2px;
    }
    .sub-title {
        text-align: center;
        color: #888888;
        font-size: 0.9em;
        margin-bottom: 40px;
    }
    .rank-tag { 
        color: #d4af37; /* 金黃色標籤 */
        font-weight: bold; 
        font-size: 0.85em; 
        letter-spacing: 1px;
        margin-bottom: 10px; 
    }
    .hot-badge { 
        background-color: #2c2c2c; 
        color: #ffd700; 
        padding: 5px 15px; 
        border-radius: 5px; 
        font-size: 0.85em; 
        font-weight: 600;
        border: 1px solid #444;
    }
    /* 新聞連結顏色：亮白，滑過變金黃 */
    a { 
        text-decoration: none !important; 
        color: #ffffff !important; 
    }
    a:hover { 
        color: #d4af37 !important; 
    }
    h3 {
        margin-top: 5px !important;
        line-height: 1.5;
        font-size: 1.2em;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>📡 資策會輿情熱度觀測站</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>2026 年度輿情自動化分析儀表板</p>", unsafe_allow_html=True)

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

        # 3. 顯示卡片清單
        for i, (_, row) in enumerate(hot_counts.head(15).iterrows()):
            title = row[col_title]
            count = row['count']
            link = df[df[col_title] == title][col_link].values[0]
            
            # 獎牌圖示與標籤
            medal = "🏆 FIRST" if i == 0 else "🥈 SECOND" if i == 1 else "🥉 THIRD" if i == 2 else f"TOP {i+1}"
            
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-tag">{medal} — TRENDING NOW</div>
                    <a href="{link}" target="_blank"><h3>{title}</h3></a>
                    <div style="margin-top: 15px;">
                        <span class="hot-badge">🔥 報導熱度：{count} 次</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ 讀取發生錯誤。錯誤訊息: {e}")
