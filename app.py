import streamlit as st
import pandas as pd

# 1. 頁面風格設定
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    .news-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        border: 1px solid #e0e0e0; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .rank-tag { color: #8d6e63; font-weight: bold; font-size: 0.9em; margin-bottom: 5px; }
    .hot-badge { background-color: #f5f5f5; color: #616161; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; }
    a { text-decoration: none !important; color: #2c3e50 !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #4e342e;'>📡 資策會輿情熱度觀測站</h2>", unsafe_allow_html=True)

# 2. 數據處理 (指向你的新 ID)
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取資料並跳過可能有問題的日期解析
    df = pd.read_csv(csv_url)
    
    if df.empty:
        st.warning("⚠️ 試算表中目前沒有資料，請執行 n8n 流程。")
    else:
        # 直接抓取第三欄(標題)與第四欄(連結)進行統計
        col_title = df.columns[2]
        col_link = df.columns[3]
        
        # 移除空值並統計標題出現次數 (不進行日期過濾，確保資料顯示)
        hot_counts = df[col_title].value_counts().reset_index()
        hot_counts.columns = [col_title, 'count']

        st.success(f"✅ 已成功讀取 {len(df)} 筆輿情資料")

        # 3. 顯示卡片清單
        for i, (_, row) in enumerate(hot_counts.head(15).iterrows()):
            title = row[col_title]
            count = row['count']
            # 取得對應連結
            link = df[df[col_title] == title][col_link].values[0]
            
            medal = "🏆 " if i == 0 else "🥈 " if i == 1 else "🥉 " if i == 2 else f"NO.{i+1} "
            
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-tag">{medal} TOP TRENDING</div>
                    <a href="{link}" target="_blank"><h3>{title}</h3></a>
                    <span class="hot-badge">📊 媒體露出次數：{count} 次</span>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ 無法讀取資料。請確認試算表已『發佈到網路』。錯誤訊息: {e}")
