import streamlit as st
import pandas as pd

st.set_page_config(page_title="資策會新聞觀測站", layout="wide")
st.title("🛡️ 資策會每周新聞觀測系統")

# 你的試算表網址 (請確保已開啟「知道連結的人均可查看」)
sheet_url = "https://docs.google.com/spreadsheets/d/1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck/edit?usp=sharing"

# 自動轉化為 CSV 下載連結的邏輯
def get_csv_url(url):
    try:
        base_url = url.split('/edit')[0]
        return f"{base_url}/export?format=csv"
    except:
        return None

csv_url = get_csv_url(sheet_url)

if csv_url:
    try:
        # 讀取資料
        df = pd.read_csv(csv_url)
        
        # 數據概況面板
        st.metric("本週追蹤新聞總數", len(df))
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("📌 各部門曝光佔比")
            # 這裡對應你在 n8n 表單裡設定的欄位名稱 (例如：'部門' 或 'department')
            target_col = '部門' if '部門' in df.columns else df.columns[-1]
            st.pie_chart(df[target_col].value_counts())
            
        with col2:
            st.subheader("📰 最新新聞清單")
            st.dataframe(df, use_container_width=True)
            
    except Exception as e:
        st.error(f"讀取資料時發生錯誤：{e}")
        st.info("請檢查：1. Google Sheets 是否已開啟『知道連結的人均可查看』。 2. 試算表內是否已有 n8n 寫入的資料。")
