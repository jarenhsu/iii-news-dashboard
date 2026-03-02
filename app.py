import streamlit as st
import pandas as pd

# 1. 頁面風格設定 (淺色溫和、高質感配色)
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    /* 整體背景：溫潤的淺米灰色 */
    .stApp {
        background-color: #fcfcf9;
        color: #37474f;
    }
    /* 卡片樣式：純白、細緻陰影、懸浮微動 */
    .news-card {
        background-color: #ffffff; 
        padding: 28px; 
        border-radius: 12px;
        border: 1px solid #f0f0ed; 
        margin-bottom: 22px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .news-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.06);
        border-color: #d1b894;
    }
    /* 標題色彩：深冷灰色 */
    .main-title {
        text-align: center; 
        color: #263238; 
        font-weight: 800;
        margin-bottom: 8px;
        letter-spacing: 1px;
    }
    .sub-title {
        text-align: center;
        color: #90a4ae;
        font-size: 0.95em;
        margin-bottom: 45px;
        font-weight: 400;
    }
    /* 標籤色彩：沉穩的咖啡金 */
    .rank-tag { 
        color: #af946d; 
        font-weight: bold; 
        font-size: 0.88em; 
        letter-spacing: 1.2px;
        margin-bottom: 12px; 
    }
    .hot-badge { 
        background-color: #f7f7f2; 
        color: #8d6e63; 
        padding: 6px 16px; 
        border-radius: 4px; 
        font-size: 0.85em; 
        font-weight: 600;
        border: 1px solid #e0e0d8;
    }
    /* 連結顏色：深色，滑過轉為暖金色 */
    a { 
        text-decoration: none !important; 
        color: #263238 !important; 
    }
    a:hover { 
        color: #af946d !important; 
    }
    h3 {
        margin-top: 5px !important;
        line-height: 1.5;
        font-size: 1.25em;
        font-weight: 700;
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
            medal = "🥇 CHAMPION" if i == 0 else "🥈 SILVER" if i == 1 else "🥉 BRONZE" if i == 2 else f"TOP {i+1}"
            
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-tag">{medal} — TRENDING NOW</div>
                    <a href="{link}" target="_blank"><h3>{title}</h3></a>
                    <div style="margin-top: 15px;">
                        <span class="hot-badge">📈 報導熱度：{count} 次</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ 讀取發生錯誤。錯誤訊息: {e}")
