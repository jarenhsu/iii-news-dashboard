import streamlit as st
import pandas as pd

# 1. 基礎網頁設定
st.set_page_config(page_title="資策會新聞觀測戰術板", layout="wide")
st.title("📊 資策會每周新聞露出戰情室")

# 2. 數據對接
SHEET_ID = "1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取資料
    df = pd.read_csv(csv_url).dropna(subset=[pd.read_csv(csv_url).columns[1]])
    
    # --- 關鍵修正：自動抓取正確欄位 ---
    # 根據你的 n8n 設定，通常順序是：0:時間, 1:標題, 2:連結, 最後一欄:部門
    # 我們強制指定位置，確保不會抓錯
    col_title = df.columns[1] # 強制抓取第 2 欄作為標題
    col_link = df.columns[2]  # 強制抓取第 3 欄作為連結
    col_dept = df.columns[-1] # 強制抓取最後一欄作為部門

    # --- 第一區：橫向長條圖 ---
    st.subheader("🏢 每周各部門新聞露出總數")
    dept_counts = df[col_dept].value_counts().sort_values(ascending=True)
    st.bar_chart(dept_counts, horizontal=True, height=400)
    
    # 顯示數字標籤
    cols_stats = st.columns(len(dept_counts))
    for i, (name, val) in enumerate(dept_counts.items()):
        with cols_stats[i]:
            st.metric(label=name, value=val)

    st.markdown("---")

    # --- 第二區：焦點新聞卡片 (修正標題位置) ---
    st.subheader("🔥 本周焦點新聞回顧 (Top 3)")
    top_3 = df.head(3) 
    
    cols = st.columns(3)
    for i, (index, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            st.image("https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80", use_container_width=True)
            
            # 這裡就是修正處：確保顯示的是 row[col_title] 而非 row[0]
            st.markdown(f"### {row[col_title]}") 
            st.warning(f"📌 **{row[col_dept]}**")
            st.link_button("👉 閱讀全文", row[col_link])

    st.markdown("---")
    
    with st.expander("🔍 點擊展開：查看所有 100 條新聞數據"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"讀取失敗：{e}")
