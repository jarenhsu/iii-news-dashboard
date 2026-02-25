import streamlit as st
import pandas as pd

# 頁面設定
st.set_page_config(page_title="資策會新聞觀測站", layout="wide")
st.title("📡 資策會輿情熱度清單")

# 試算表 CSV 連結 (請確認 SHEET_ID 是否正確)
SHEET_ID = "1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取資料
    raw_df = pd.read_csv(csv_url)
    # 取得標題欄位 (索引 2) 並去除空值
    df = raw_df.dropna(subset=[raw_df.columns[2]])
    
    # 統計熱度
    col_title = df.columns[2]
    col_link = df.columns[3]
    hot_counts = df[col_title].value_counts().reset_index()
    hot_counts.columns = [col_title, '露出次數']

    st.markdown(f"#### 💡 今日偵測到 {len(hot_counts)} 則獨特新聞")
    st.divider()

    # 顯示列表
    for i, (_, row) in enumerate(hot_counts.head(20).iterrows()):
        title = row[col_title]
        count = row['露出次數']
        # 取得該新聞的第一個連結
        link = df[df[col_title] == title][col_link].values[0]
        
        # 標出 Top 3 的獎牌
        medal = "🥇 " if i == 0 else "🥈 " if i == 1 else "🥉 " if i == 2 else "🔹 "
        
        # 用簡單的列式呈現
        st.markdown(f"{medal} **[{title}]({link})**")
        st.caption(f"報導熱度：{count} 家媒體露出")
        st.write("") # 增加間距

except Exception as e:
    st.error("暫時無法讀取資料，請確認 Google Sheets 內容已更新。")
