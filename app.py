import streamlit as st
import pandas as pd

# 1. 基礎網頁設定
st.set_page_config(page_title="資策會新聞行動戰情室", layout="wide")
st.markdown("### 📊 資策會每周新聞露出戰情室")

# 2. 數據對接
SHEET_ID = "1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取資料
    df = pd.read_csv(csv_url).dropna(subset=[pd.read_csv(csv_url).columns[1]])
    
    # 欄位對位修正 (C1 是標題)
    col_title = df.columns[2] # C欄: 標題
    col_link = df.columns[3]  # D欄: 連結
    col_dept = df.columns[-1] # 最後一欄: 部門

    # --- 第一區：各部門總數 (手機優化圖表) ---
    st.write("🏢 **各部門本周露出總數**")
    dept_counts = df[col_dept].value_counts().sort_values(ascending=True)
    st.bar_chart(dept_counts, horizontal=True, height=300)
    
    # 數據指標卡片 (兩兩一排)
    metrics_cols = st.columns(2) 
    for i, (name, val) in enumerate(dept_counts.sort_values(ascending=False).items()):
        metrics_cols[i % 2].metric(label=name, value=val)

    st.markdown("---")

    # --- 第二區：焦點新聞卡片 (圖片回歸 + 手機優化) ---
    st.write("🔥 **本周焦點新聞回顧 (Top 3)**")
    top_3 = df.head(3)
    
    for index, row in top_3.iterrows():
        # 使用容器建立卡片感
        with st.container(border=True):
            # 1. 顯示圖片 (這行加回來了，使用寬度自適應)
            st.image("https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&q=80", use_container_width=True)
            
            # 2. 顯示標題 (加大加粗)
            st.markdown(f"#### {row[col_title]}")
            
            # 3. 顯示部門標籤
            st.warning(f"📌 分類：{row[col_dept]}")
            
            # 4. 閱讀全文按鈕 (滿版寬度，方便手機點擊)
            st.link_button("👉 閱讀全文", row[col_link], use_container_width=True)

    st.markdown("---")
    
    # 第三區：完整清單
    with st.expander("🔍 點擊展開：查看完整新聞明細"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"資料更新中，請稍候再試。")
