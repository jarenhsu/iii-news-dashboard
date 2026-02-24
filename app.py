import streamlit as st
import pandas as pd

# 1. 基礎網頁設定
st.set_page_config(page_title="資策會新聞觀測戰術板", layout="wide")
st.title("📊 資策會每周新聞露出戰情室")

# 2. 數據對接 (使用你提供的正確 ID)
SHEET_ID = "1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取資料並過濾掉空行
    df = pd.read_csv(csv_url).dropna(subset=[pd.read_csv(csv_url).columns[1]])
    
    # --- 關鍵修正：精準定位欄位位置 ---
    # 根據你的 n8n 寫入順序：
    # 第 0 欄：時間
    # 第 1 欄：新聞標題 (這是我們要修正的地方)
    # 第 2 欄：新聞連結
    # 最後一欄：部門分類
