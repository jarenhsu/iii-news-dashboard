import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. 頁面風格設定
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

# 2. 數據處理
SHEET_ID = "1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    raw_df = pd.read_csv(csv_url)
    
    # 轉換日期 (假設第一欄為 Timestamp)
    raw_df[raw_df.columns[0]] = pd.to_datetime(raw_df[raw_df.columns[0]])
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    # 篩選過去 7 天的資料
    df = raw_df[raw_df[raw_df.columns[0]] >= seven_days_ago].copy()
    
    # 統計標題出現次數 (熱度) - 假設第三欄為標題，第四欄為連結
    col_title = df.columns[2]
    col_link = df.columns[3]
    hot_counts = df[col_title].value_counts().reset_index()
    hot_counts.columns = [col_title, 'count']

    st.markdown(f"<p style='text-align: center; color: #8d6e63;'>🗓️ 統計區間：{seven_days_ago.strftime('%m/%d')} - 今日</p>", unsafe_allow_html=True)

    # 3. 顯示卡片清單
    for i, (_, row) in enumerate(hot_counts.head(15).iterrows()):
        title = row[col_title]
        count = row['count']
        link = df[df[col_title] == title][col_link].values[0]
        
        medal = "🏆 " if i == 0 else "🥈 " if i == 1 else "🥉 " if i == 2 else f"NO.{i+1} "
        
        st.markdown(f"""
            <div class="news-card">
                <div class="rank-tag">{medal} TOP TRENDING</div>
                <a href="{link}" target="_blank"><h3>{title}</h3></a>
                <span class="hot-badge">📊 過去 7 天內共 {count} 家媒體報導</span>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error("目前尚無本週輿情資料，請確認 n8n 已成功寫入 Google Sheets。")
