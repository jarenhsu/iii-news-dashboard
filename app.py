import streamlit as st
import pandas as pd

# 1. 基礎網頁設定
st.set_page_config(page_title="資策會新聞觀測戰術板", layout="wide")
st.title("📊 資策會每周新聞露出戰情室")

# 2. 數據對接
SHEET_ID = "1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取 n8n 解析出的資料
    df = pd.read_csv(csv_url).dropna(subset=[pd.read_csv(csv_url).columns[1]])
    
    # 自動辨識欄位
    col_title = df.columns[1] # 新聞名稱
    col_link = df.columns[2]  # 連結
    col_dept = df.columns[-1] # 部門

    # --- 第一區：橫向長條圖 (顯示清楚數字) ---
    st.subheader("🏢 每周各部門新聞露出總數")
    dept_counts = df[col_dept].value_counts().sort_values(ascending=True)
    
    # 使用 st.bar_chart 顯示，並利用文字顯示數值
    st.bar_chart(dept_counts, horizontal=True, height=400)
    # 小技巧：在圖表下方用數據清單顯示精確數字，更清楚
    cols_stats = st.columns(len(dept_counts))
    for i, (name, val) in enumerate(dept_counts.items()):
        with cols_stats[i]:
            st.metric(label=name, value=val)

    st.markdown("---")

    # --- 第二區：焦點新聞卡片 (新聞名稱為主，日期移除) ---
    st.subheader("🔥 本周焦點新聞回顧 (Top 3)")
    top_3 = df.head(3)
    
    cols = st.columns(3)
    for i, (index, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            # 科技風格配圖
            st.image("https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80", use_container_width=True)
            
            # 標題優先：新聞名稱
            st.markdown(f"### {row[col
