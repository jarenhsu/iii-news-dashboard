import streamlit as st
import pandas as pd

# 1. 頁面設定：簡潔手機優化版
st.set_page_config(page_title="資策會新聞熱度觀測", layout="wide")
st.markdown("### 📡 資策會本周輿情熱度排行 (Top 5)")

# 2. 數據對接 (使用你的試算表 ID)
SHEET_ID = "1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取資料並跳過空行
    df = pd.read_csv(csv_url).dropna(subset=[pd.read_csv(csv_url).columns[2]])
    
    # --- 欄位定義 ---
    # 索引說明：2=C欄(標題), 3=D欄(連結), 4=E欄(n8n 寫入的圖片網址)
    col_title = df.columns[2] 
    col_link = df.columns[3]
    # 檢查是否有 'image' 欄位，沒有則顯示預設圖
    col_img = 'image' if 'image' in df.columns else df.columns[-1]

    # --- 核心邏輯：計算新聞熱度 (相同標題出現次數) ---
    # 1. 統計每個標題出現幾次
    hot_counts = df[col_title].value_counts().reset_index()
    hot_counts.columns = [col_title, '露出次數']
    
    # 2. 合併回原始資料以取得連結與圖片網址
    top_5 = pd.merge(hot_counts.head(5), df, on=col_title, how='left').drop_duplicates(subset=[col_title])

    # --- 顯示區：前五名熱度卡片 ---
    rank_icons = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    
    for i, (index, row) in enumerate(top_5.iterrows()):
        with st.container(border=True):
            # 顯示排名與熱度數字
            st.markdown(f"{rank_icons[i]} **熱度：{row['露出次數']} 家媒體報導**")
            
            # 顯示圖片 (讀取 n8n 抓到的真實圖片)
            img_url = row[col_img] if pd.notna(row[col_img]) else "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&q=80"
            st.image(img_url, use_container_width=True)
            
            # 顯示標題
            st.markdown(f"#### {row[col_title]}")
            
            # 連結按鈕 (滿版寬度)
            st.link_button("👉 點擊查看相關報導", row[col_link], use_container_width=True)

    st.markdown("---")
    
    with st.expander("🔍 點擊展開：查看所有 100 條原始數據"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"輿情分析失敗：請確認 Google Sheets 已經透過 n8n 寫入資料，且包含標題、連結與圖片。")
