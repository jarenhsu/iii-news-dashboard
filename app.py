import streamlit as st
import pandas as pd

# 1. 基礎網頁設定
st.set_page_config(page_title="資策會新聞觀測站", layout="wide")
st.title("📊 資策會每周新聞露出戰情室")

# 2. 數據對接
SHEET_ID = "1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取資料並跳過空行
    df = pd.read_csv(csv_url).dropna(subset=[pd.read_csv(csv_url).columns[1]])
    
    # --- 關鍵修正：對應你的 C1 標題結構 ---
    # 索引說明：0=A欄(Timestamp), 1=B欄, 2=C欄(標題), 3=D欄(連結)
    col_title = df.columns[2] # 強制抓取 C 欄作為「新聞標題」
    col_link = df.columns[3]  # 強制抓取 D 欄作為「新聞連結」
    col_dept = df.columns[-1] # 強制抓取最後一欄作為「部門分類」

    # --- 第一區：橫向長條圖 (顯示清楚數字) ---
    st.subheader("🏢 每周各部門新聞露出總數")
    dept_counts = df[col_dept].value_counts().sort_values(ascending=True)
    st.bar_chart(dept_counts, horizontal=True, height=400)
    
    # 顯示各部門精確數字
    cols_stats = st.columns(len(dept_counts))
    for i, (name, val) in enumerate(dept_counts.items()):
        with cols_stats[i]:
            st.metric(label=name, value=val)

    st.markdown("---")

    # --- 第二區：Top 3 焦點新聞 (新聞名稱優先，顯示部門) ---
    st.subheader("🔥 本周焦點新聞回顧 (Top 3)")
    top_3 = df.head(3) 
    
    cols = st.columns(3)
    for i, (index, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            # 使用科技風格圖片預覽
            st.image("https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80", use_container_width=True)
            
            # 顯示正確的 C 欄標題內容
            st.markdown(f"### {row[col_title]}") 
            st.warning(f"📌 **{row[col_dept]}**")
            st.link_button("👉 閱讀全文", row[col_link])

    st.markdown("---")
    
    # 第三區：完整清單
    with st.expander("🔍 查看完整新聞數據清單"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"資料對接失敗：{e}")
