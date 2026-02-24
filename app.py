import streamlit as st
import pandas as pd

# 頁面寬度與標題設定
st.set_page_config(page_title="資策會新聞觀測站", layout="wide")
st.title("📊 資策會每周新聞露出戰情室")

# --- 數據對接 ---
SHEET_ID = "1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取 n8n 解析出的資料
    df = pd.read_csv(csv_url)
    
    # 1. 每週各部門新聞總數 (長條圖)
    st.subheader("🏢 各部門本週露出總數")
    dept_col = df.columns[-1] # 自動抓取最後一欄分類
    dept_counts = df[dept_col].value_counts().reset_index()
    dept_counts.columns = ['部門', '露出次數']
    st.bar_chart(dept_counts.set_index('部門'))

    st.markdown("---")

    # 2. 本週焦點：Top 3 新聞預覽
    st.subheader("🔥 本週最熱門新聞 (Top 3)")
    # 註：由於 Google News RSS 不直接提供點擊數，我們以清單前三則作為焦點推薦
    top_3 = df.head(3)
    
    cols = st.columns(3)
    for i, (index, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            # 建立像卡片一樣的預覽
            st.info(f"**{row.get('部門', '綜合')}**")
            st.markdown(f"### {row['title']}") # 標題
            st.caption(f"📅 發布日期：{row['date']}") # 日期
            
            # 這裡我們利用新聞連結產生一個簡易的「查看原文」按鈕
            st.link_button("閱讀新聞全文", row['link']) # 連結

    st.markdown("---")

    # 3. 完整數據表搜尋
    with st.expander("🔍 查看所有新聞明細"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"儀表板更新失敗：{e}")
