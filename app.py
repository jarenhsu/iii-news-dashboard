import streamlit as st
import pandas as pd

# 1. 頁面風格設定 (淺色溫和質感)
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    /* 整體背景：溫和的淺灰色 */
    .stApp {
        background-color: #f9f9f7;
        color: #333;
    }
    /* 卡片樣式：白底、柔和陰影、圓角 */
    .news-card {
        background-color: #ffffff; 
        padding: 30px; 
        border-radius: 12px;
        border: 1px solid #eef0f2; 
        margin-bottom: 25px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: transform 0.2s ease-in-out;
    }
    .news-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    }
    /* 標題設定：深藍灰色 */
    .main-title {
        text-align: center; 
        color: #2c3e50; 
        font-weight: 800;
        font-size: 2.2em;
        margin-top: 20px;
    }
    .sub-title {
        text-align: center;
        color: #7f8c8d;
        font-size: 1em;
        margin-bottom: 40px;
        letter-spacing: 2px;
    }
    /* 排名文字：溫潤的咖啡金 */
    .rank-text { 
        color: #bfa17a; 
        font-weight: 900; 
        font-size: 1.6em; 
        margin-bottom: 10px; 
    }
    .news-title { 
        font-size: 1.4em; 
        font-weight: 700; 
        color: #2c3e50; 
        margin: 10px 0; 
        line-height: 1.5; 
    }
    .source-container { 
        margin-top: 20px; 
        padding-top: 15px; 
        border-top: 1px solid #f1f1f1; 
    }
    /* 按鈕樣式：淺灰底、深藍灰字 */
    .source-btn {
        display: inline-block; 
        background-color: #f4f6f7; 
        color: #566573 !important;
        padding: 7px 16px; 
        border-radius: 6px; 
        font-size: 0.85em;
        margin: 5px; 
        border: 1px solid #d5dbdb; 
        text-decoration: none; 
        transition: 0.2s;
    }
    .source-btn:hover { 
        background-color: #ebedef; 
        border-color: #bdc3c7;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-title'>📡 資策會輿情熱度觀測站</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>WEEKLY TRENDING REPORT</div>", unsafe_allow_html=True)

# 2. 數據處理
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python')
    
    # 鎖定：第3欄標題，第4欄連結
    df['title'] = df.iloc[:, 2].astype(str).str.replace(r'\n', '', regex=True).str.strip()
    df['link'] = df.iloc[:, 3].astype(str).str.strip()

    df = df[df['title'].str.len() > 2] 
    df = df[~df['title'].str.contains("新聞標題")]

    grouped = df.groupby('title')['link'].apply(list).reset_index()
    grouped['count'] = grouped['link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    if grouped.empty:
        st.info("💡 目前資料同步中，請稍候。")
    else:
        for i, (_, row) in enumerate(grouped.iterrows()):
            title = row['title']
            links = row['link']
            count = row['count']
            
            # 排名設計
            medal = "🥇 CHAMPION" if i == 0 else "🥈 SILVER" if i == 1 else "🥉 BRONZE" if i == 2 else f"TOP {i+1}"
            
            # 生成來源按鈕
            links_html = "".join([f'<a class="source-btn" href="{u}" target="_blank">🌐 來源 {idx+1}</a>' for idx, u in enumerate(links) if 'http' in str(u)])
            
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-text">{medal}</div>
                    <div class="news-title">{title}</div>
                    <div style="color: #95a5a6; font-size: 0.9em; margin-bottom: 10px; font-weight: 600;">📈 本週報導熱度：{count} 次</div>
                    <div class="source-container">
                        <div style="color: #bdc3c7; font-size: 0.8em; margin-bottom: 10px;">🔗 相關報導連結：</div>
                        {links_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"系統資料校準中。")
