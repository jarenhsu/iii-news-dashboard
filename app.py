# 關鍵修正：確保讀取 Google Sheets 時能對應到正確的欄位
# 程式會自動計算出現次數最多的標題作為「熱門新聞」
import streamlit as st
import pandas as pd

st.set_page_config(page_title="資策會新聞熱度觀測", layout="wide")
st.markdown("### 📡 資策會輿情熱度排行 (Top 5)")

SHEET_ID = "1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(csv_url)
    # 自動統計標題出現次數 (熱度)
    hot_counts = df.iloc[:, 2].value_counts().reset_index()
    hot_counts.columns = ['標題', '露出次數']
    
    # 顯示前五名
    for i in range(min(5, len(hot_counts))):
        row = hot_counts.iloc[i]
        with st.container(border=True):
            st.write(f"排名 {i+1}：{row['標題']} ({row['露出次數']} 次報導)")
            # 這裡會讀取你 n8n 寫入的最後一欄 (image)
            st.image(df[df.iloc[:, 2] == row['標題']].iloc[0, -1]) 
except Exception as e:
    st.error("請確認 Google Sheets 資料已由 n8n 更新並包含 image 欄位")
