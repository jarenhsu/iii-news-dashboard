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

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 💡 讀取資料
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python')

    # 🚀 自動防撞核心：檢查欄位數量
    # 如果欄位不足 5 個，自動補足空白欄位，防止 iloc[:, 4] 崩潰
    while df.shape[1] < 5:
        df[f'extra_col_{df.shape[1]}'] = "媒體報導"

    # 使用 iloc 鎖定資料 (這時保證不會崩潰)
    df['c_date'] = df.iloc[:, 1].fillna("近期").astype(str)
    df['c_title'] = df.iloc[:, 2].fillna("未知標題").astype(str).str.replace(r'\n', '', regex=True)
    df['c_link'] = df.iloc[:, 3].fillna("").astype(str)
    df['c_media'] = df.iloc[:, 4].fillna("媒體報導").astype(str)

    # 數據過濾
    df = df[df['c_title'].str.len() > 5]
    df = df[~df['c_title'].str.contains("標題")]

    # 聚合與排序
    grouped = df.groupby('c_title').agg({'c_link': list, 'c_media': list, 'c_date': 'max'}).reset_index()
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    # 顯示結果
    for i, (_, row) in enumerate(grouped.iterrows()):
        st.markdown(f"""
            <div class="news-card">
                <div class="rank-text">TOP {i+1} RANKING</div>
                <div class="topic-title">{row['c_title']}</div>
                <div class="info-bar">📅 最新日期：{row['c_date']} ｜ 🔥 露出：{row['count']} 次</div>
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander(f"📂 查看 {row['count']} 家媒體來源"):
            for m, l in zip(row['c_media'], row['c_link']):
                st.write(f"**[{m}]** ➔ [連結]({l})")

except Exception as e:
    st.info("🔄 資料同步中，請確保 n8n 已完成首次媒體名稱寫入。")
