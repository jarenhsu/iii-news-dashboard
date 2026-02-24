import streamlit as st
import pandas as pd

st.set_page_config(page_title="資策會新聞觀測站", layout="wide")
st.title("📊 資策會每周新聞露出戰情室")

# 數據對接 (使用你提供的正確 ID)
SHEET_ID = "1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取 n8n 寫入的資料
    df = pd.read_csv(csv_url).dropna(how='all')
    
    # --- 自動辨識欄位名稱 ---
    # 假設：第1欄是日期, 第2欄是標題, 第3欄是連結, 最後1欄是部門
    col_date = df.columns[0]
    col_title = df.columns[1]
    col_link = df.columns[2]
    col_dept = df.columns[-1]

    # 1. 橫向長條圖
    st.subheader("🏢 每周各部門新聞露出總數")
    dept_counts = df[col_dept].value_counts().sort_values(ascending=True)
    st.bar_chart(dept_counts, horizontal=True, height=400)

    st.markdown("---")

    # 2. Top 3 焦點新聞 (使用自動辨識的欄位)
    st.subheader("🔥 本周最受關注新聞 (Top 3)")
    top_3 = df.head(3)
    
    cols = st.columns(3)
    for i, (index, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            st.image("https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80", use_container_width=True)
            st.warning(f"**{row[col_dept]}**")
            st.markdown(f"#### {row[col_title]}") # 這裡改用自動辨識的標題欄位
            st.caption(f"📅 {row[col_date]}")
            st.link_button("👉 閱讀新聞全文", row[col_link])

    st.markdown("---")
    
    with st.expander("🔍 點擊展開：查看完整新聞清單明細"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"儀表板讀取失敗：{e}")
