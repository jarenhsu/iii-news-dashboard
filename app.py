import streamlit as st
import pandas as pd

# 1. 針對手機螢幕寬度優化
st.set_page_config(page_title="資策會新聞行動戰情室", layout="wide")

# 使用 Markdown 縮小手機端標題字體，避免換行太亂
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

    # --- 第一區：各部門總數 (手機端數字垂直排列) ---
    st.write("🏢 **各部門本周露出總數**")
    dept_counts = df[col_dept].value_counts().sort_values(ascending=True)
    
    # 調降圖表高度，避免在手機上佔據整屏
    st.bar_chart(dept_counts, horizontal=True, height=300)
    
    # 手機端建議使用 columns 讓數字兩兩一排
    metrics_cols = st.columns(2) 
    for i, (name, val) in enumerate(dept_counts.sort_values(ascending=False).items()):
        metrics_cols[i % 2].metric(label=name, value=val)

    st.markdown("---")

    # --- 第二區：焦點新聞 (手機端自動堆疊) ---
    st.write("🔥 **本周焦點新聞回顧 (Top 3)**")
    top_3 = df.head(3)
    
    # 在手機上 st.columns(3) 會自動轉為垂直堆疊，這點很棒
    for index, row in top_3.iterrows():
        # 使用一個容器(Container)包裹每則新聞，增加層次感
        with st.container(border=True):
            # 新聞標題放在最上面
            st.markdown(f"**{row[col_title]}**")
            # 顯示部門標籤
            st.caption(f"📌 分類：{row[col_dept]}")
            # 連結按鈕加大，方便手機點擊
            st.link_button("閱讀全文", row[col_link], use_container_width=True)

    st.markdown("---")
    
    # 第三區：完整清單 (手機端預設收納)
    with st.expander("🔍 完整數據清單"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"資料讀取失敗，請確認網路連線或權限設定。")
