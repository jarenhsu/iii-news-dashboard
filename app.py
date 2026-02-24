import streamlit as st
import pandas as pd

# 1. 基礎網頁設定
st.set_page_config(page_title="資策會新聞觀測站", layout="wide")
st.title("📊 資策會每周新聞露出戰情室")

# 2. 數據對接 (使用你提供的正確 ID)
SHEET_ID = "1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取資料並自動清理空行
    df = pd.read_csv(csv_url).dropna(subset=[pd.read_csv(csv_url).columns[1]])
    
    # --- 關鍵修正：精準定位欄位 ---
    # 根據你的 n8n 寫入畫面：
    # 第 0 欄通常是 Timestamp (自動產生的時間)
    # 第 1 欄才是你抓的 'title' (新聞名稱)
    # 第 2 欄是 'link' (新聞連結)
    # 最後一欄是 'department' (部門分類)
    
    col_title = df.columns[1] # 指定抓取第二欄作為標題
    col_link = df.columns[2]  # 指定抓取第三欄作為連結
    col_dept = df.columns[-1] # 指定抓取最後一欄作為部門

    # --- 第一區：橫向長條圖 (顯示數字) ---
    st.subheader("🏢 每周各部門新聞露出總數")
    dept_counts = df[col_dept].value_counts().sort_values(ascending=True)
    st.bar_chart(dept_counts, horizontal=True, height=400)
    
    # 在圖表下方顯示精確數字
    cols_stats = st.columns(len(dept_counts))
    for i, (name, val) in enumerate(dept_counts.items()):
        with cols_stats[i]:
            st.metric(label=name, value=val)

    st.markdown("---")

    # --- 第二區：Top 3 焦點新聞 (修正標題顯示) ---
    st.subheader("🔥 本周焦點新聞回顧 (Top 3)")
    top_3 = df.head(3) 
    
    cols = st.columns(3)
    for i, (index, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            # 科技風格預設圖
            st.image("https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80", use_container_width=True)
            
            # 標題修正點：確保顯示 row[col_title]
            st.markdown(f"### {row[col_title]}") 
            st.warning(f"📌 **{row[col_dept]}**")
            st.link_button("👉 閱讀全文", row[col_link])

    st.markdown("---")
    
    # 完整數據明細
    with st.expander("🔍 點擊展開：查看所有 100 條新聞原始數據"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"讀取失敗：{e}")
