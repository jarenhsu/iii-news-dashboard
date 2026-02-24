import streamlit as st
import pandas as pd

st.set_page_config(page_title="資策會新聞觀測站", layout="wide")
st.title("🛡️ 資策會每周新聞觀測系統")

# --- 自動對接你的試算表 ---
SHEET_ID = "1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取 n8n 寫入的 100 條資料
    df = pd.read_csv(csv_url)
    
    # 頁面指標
    st.metric("本週追蹤新聞總數", len(df))
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📌 各部門曝光佔比")
        # 自動抓取最後一欄（n8n 分類的部門）
        dept_col = df.columns[-1] 
        st.bar_chart(df[dept_col].value_counts())
        
    with col2:
        st.subheader("📰 最新新聞清單")
        # 顯示所有新聞明細
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"連線失敗：{e}")
    st.info("提示：請檢查你的 Google Sheets 是否已開啟『知道連結的人均可查看』權限。")
