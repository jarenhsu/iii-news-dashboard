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
    # 讀取資料並忽略解析錯誤
    raw_df = pd.read_csv(csv_url)
    
    # 強制轉換第一欄為日期，處理各種格式
    raw_df[raw_df.columns[0]] = pd.to_datetime(raw_df[raw_df.columns[0]], errors='coerce')
    
    # 移除日期解析失敗的列
    raw_df = raw_df.dropna(subset=[raw_df.columns[0]])
    
    # 篩選過去 7 天的資料 (如果資料太少，自動擴展到 14 天)
    seven_days_ago = datetime.now() - timedelta(days=7)
    df = raw_df[raw_df[raw_df.columns[0]] >= seven_days_ago].copy()
    
    # 💡 保險機制：如果過去 7 天沒資料，就顯示所有資料，避免白屏
    if df.empty:
        df = raw_df.copy()
        st.info("💡 目前 7 天內尚無新資料，為您顯示所有歷史記錄。")

    # 統計標題熱度 (假設第三欄為標題，第四欄為連結)
    col_title = df.columns[2]
    col_link = df.columns[3]
    hot_counts = df[col_title].value_counts().reset_index()
    hot_counts.columns = [col_title, 'count']

    # 3. 顯示卡片列表
    for i, (_, row) in enumerate(hot_counts.head(15).iterrows()):
        title = row[col_title]
        count = row['count']
        link = df[df[col_title] == title][col_link].values[0]
        
        medal = "🏆 " if i == 0 else "🥈 " if i == 1 else "🥉 " if i == 2 else f"NO.{i+1} "
        
        st.markdown(f"""
            <div class="news-card">
                <div class="rank-tag">{medal} TOP TRENDING</div>
                <a href="{link}" target="_blank"><h3>{title}</h3></a>
                <span class="hot-badge">📊 累積報導熱度：{count} 次</span>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"資料讀取失敗，請確認 n8n 已成功寫入 Google Sheets 並包含日期欄位。")
