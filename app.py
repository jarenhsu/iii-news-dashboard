import streamlit as st
import pandas as pd

# 1. 網頁基礎設定
st.set_page_config(page_title="資策會新聞觀測站", layout="wide")
st.title("📊 資策會每周新聞露出戰情室")

# 2. 數據對接
SHEET_ID = "1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取 n8n 寫入的資料
    df = pd.read_csv(csv_url)
    
    # 清理資料：刪除全空的行，確保統計正確
    df = df.dropna(subset=[df.columns[1]]) 

    # --- 第一區：橫向長條圖 (文字最清晰) ---
    st.subheader("🏢 每周各部門新聞露出總數")
    
    # 自動抓取最後一個欄位（部門分類）
    dept_col = df.columns[-1] 
    # 排序：讓數量最多的排在上面
    dept_counts = df[dept_col].value_counts().sort_values(ascending=True) 
    
    # 關鍵設定：horizontal=True 讓長條圖變橫的，height 增加高度讓文字不擁擠
    st.bar_chart(dept_counts, horizontal=True, height=400)

    st.markdown("---")

    # --- 第二區：Top 3 焦點新聞預覽 ---
    st.subheader("🔥 本周最受關注新聞 (Top 3)")
    top_3 = df.head(3) # 抓取前三筆最新新聞
    
    cols = st.columns(3)
    for i, (index, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            # 使用科技感的預設縮圖
            st.image("https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80", use_container_width=True)
            st.warning(f"**{row[dept_col]}**") # 顯示部門標籤
            st.markdown(f"#### {row['title']}") # 標題
            st.caption(f"📅 {row['date']}") # 日期
            st.link_button("👉 閱讀新聞全文", row['link']) # 連結

    st.markdown("---")
    
    # --- 第三區：數據明細 ---
    with st.expander("🔍 點擊展開：查看完整新聞清單明細"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"資料讀取失敗：{e}")
    st.info("提示：請確認您的 Google Sheets 是否已開啟『知道連結的人均可查看』權限。")
