import streamlit as st
import pandas as pd

st.set_page_config(page_title="資策會新聞觀測站", layout="wide")
st.title("🛡️ 資策會每周新聞觀測系統")

# --- 設定區 ---
# 請在此貼上你的 Google Sheets 網址
sheet_url = "https://docs.google.com/spreadsheets/d/1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck/edit?usp=sharing"

def get_csv_url(url):
    try:
        # 將 /edit 改為 /export?format=csv 以便程式讀取
        if "/edit" in url:
            return url.split("/edit")[0] + "/export?format=csv"
        return url
    except:
        return None

csv_url = get_csv_url(sheet_url)

# --- 讀取與顯示 ---
if csv_url:
    try:
        # 讀取 CSV
        df = pd.read_csv(csv_url)
        
        if not df.empty:
            # 數據儀表板
            st.metric("本週追蹤新聞總數", len(df))
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader("📌 各部門曝光佔比")
                # 自動抓取最後一欄（通常是 n8n 分類的部門）
                target_col = df.columns[-1]
                st.pie_chart(df[target_col].value_counts())
                
            with col2:
                st.subheader("📰 最新新聞清單")
                st.dataframe(df, use_container_width=True)
        else:
            st.info("試算表目前是空的，請確認 n8n 是否已成功寫入資料。")
            
    except Exception as e:
        st.error(f"連線失敗：{e}")
        st.info("請檢查 Google Sheets 是否已開啟『知道連結的人均可查看』。")
else:
    st.warning("請在 app.py 中填入正確的 Google Sheets 網址。")
