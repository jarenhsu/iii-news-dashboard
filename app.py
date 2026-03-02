import streamlit as st
import pandas as pd

# 1. 頁面風格設定
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcf9; color: #37474f; }
    .news-card {
        background-color: #ffffff; padding: 25px; border-radius: 12px;
        border: 1px solid #f0f0ed; margin-bottom: 25px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }
    .rank-text { color: #af946d; font-weight: 900; font-size: 1.5em; margin-bottom: 5px; }
    .topic-title { font-size: 1.4em; font-weight: 700; color: #2c3e50; margin-bottom: 15px; }
    .info-bar { margin-bottom: 15px; font-size: 0.85em; color: #95a5a6; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-title'>📡 資策會輿情熱度觀測站</div>", unsafe_allow_html=True)

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取資料
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("未知")

    # 💡 這次改用最保險的「順序對位」：
    # 假設 n8n 寫入順序是：A(時間戳記), B(日期), C(標題), D(連結), E(媒體名稱)
    # 我們直接指定索引，避開名稱偵測失敗的問題
    df['c_date'] = df.iloc[:, 1].astype(str).str.strip()   # 第二欄：日期
    df['c_title'] = df.iloc[:, 2].astype(str).str.strip()  # 第三欄：標題
    df['c_link'] = df.iloc[:, 3].astype(str).str.strip()   # 第四欄：連結
    df['c_media'] = df.iloc[:, 4].astype(str).str.strip()  # 第五欄：媒體名稱

    # 排除雜訊
    df = df[df['c_title'].str.len() > 5]
    df = df[~df['c_title'].str.contains("標題")]

    # 聚合
    grouped = df.groupby('c_title').agg({
        'c_link': list, 
        'c_media': list, 
        'c_date': 'max'
    }).reset_index()
    
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    for i, (_, row) in enumerate(grouped.iterrows()):
        st.markdown(f"""
            <div class="news-card">
                <div class="rank-text">TOP {i+1}</div>
                <div class="topic-title">{row['c_title']}</div>
                <div class="info-bar">📅 最新日期：{row['c_date']} ｜ 🔥 累計露出：{row['count']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander(f"📂 查看 {row['count']} 家媒體來源"):
            for m, l in zip(row['c_media'], row['c_link']):
                st.write(f"**[{m}]** ➔ [閱讀原文]({l})")

except Exception as e:
    # 💡 這裡會顯示真正的錯誤，方便我們除錯
    st.error(f"❌ 讀取失敗！原因：{e}")
    st.info("請檢查 Google 試算表是否至少有 5 欄資料（日期、標題、連結、媒體）。")
