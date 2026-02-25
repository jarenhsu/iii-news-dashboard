import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. 頁面風格設定 (質感卡片佈局)
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    .news-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .rank-tag { color: #8d6e63; font-weight: bold; font-size: 0.9em; margin-bottom: 5px; }
    .hot-badge { background-color: #f5f5f5; color: #616161; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; }
    a { text-decoration: none !important; color: #2c3e50 !important; }
    a:hover { color: #8d6e63 !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #4e342e;'>📡 資策會本週輿情熱度排行</h2>", unsafe_allow_html=True)

# 2. 數據處理 (使用新 ID)
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取資料
    df = pd.read_csv(csv_url)
    
    # 強制解析時間戳記 (第一欄)
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
    df = df.dropna(subset=[df.columns[0]])
    
    # 篩選過去 7 天的資料
    limit_date = datetime.now() - timedelta(days=7)
    recent_df = df[df.iloc[:, 0] >= limit_date].copy()
    
    # 如果 7 天內沒資料則顯示全部 (保險機制)
    if recent_df.empty:
        st.info("💡 過去 7 天內尚無新資料，為您顯示所有歷史記錄。")
        recent_df = df.copy()

    # 統計標題熱度 (假設第三欄是標題，第四欄是連結)
    col_title = df.columns[2]
    col_link = df.columns[3]
    hot_counts = recent_df[col_title].value_counts().reset_index()
    hot_counts.columns = [col_title, 'count']

    # 3. 顯示卡片清單 (最多顯示前 15 名)
    for i, (_, row) in enumerate(hot_counts.head(15).iterrows()):
        title = row[col_title]
        count = row['count']
        # 取得該標題對應的第一個連結
        link = recent_df[recent_df[col_title] == title][col_link].values[0]
        
        medal = "🏆 " if i == 0 else "🥈 " if i == 1 else "🥉 " if i == 2 else f"NO.{i+1} "
        
        st.markdown(f"""
            <div class="news-card">
                <div class="rank-tag">{medal} TOP TRENDING</div>
                <a href="{link}" target="_blank"><h3>{title}</h3></a>
                <span class="hot-badge">📊 報導熱度：{count} 次</span>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error("目前尚無輿情資料，請確保試算表已發佈到網路且包含新聞數據。")
