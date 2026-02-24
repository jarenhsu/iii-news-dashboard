import streamlit as st
import pandas as pd

st.set_page_config(page_title="資策會新聞觀測站", layout="wide")
st.title("📊 資策會每周新聞露出戰情室")

# --- 數據對接 ---
SHEET_ID = "1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取 n8n 寫入的 100 條資料
    df = pd.read_csv(csv_url)
    
    # 1. 顯示每周各部門露出總數
    st.subheader("🏢 每周各部門新聞露出總數")
    dept_col = df.columns[-1] # 自動抓取 n8n 分類的最後一欄
    dept_counts = df[dept_col].value_counts()
    st.bar_chart(dept_counts)

    st.markdown("---")

    # 2. 最多人觀看的 3 則新聞 (以清單前三則作為焦點)
    st.subheader("🔥 本周焦點新聞回顧")
    top_3 = df.head(3)
    
    cols = st.columns(3)
    for i, (index, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            # 使用預設科技圖片美化畫面
            st.image("https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=400", use_container_width=True)
            st.markdown(f"**[{row.get(dept_col, '綜合')}]**") # 顯示分類部門
            st.markdown(f"#### {row['title']}") # 顯示標題
            st.caption(f"📅 {row['date']}") # 顯示日期
            st.link_button("👉 查看全文", row['link']) # 點擊連結

    st.markdown("---")
    
    # 3. 完整數據搜尋表
    with st.expander("🔍 點擊展開：查看完整新聞明細表"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"儀表板讀取失敗：{e}")
