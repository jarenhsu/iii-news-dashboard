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
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("媒體報導")

    # 智慧識別欄位
    col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), None)
    col_date = next((c for c in df.columns if df[c].astype(str).str.match(r'\d{4}-\d{2}-\d{2}').any()), None)
    
    # 媒體欄：通常是字數較短且非日期的欄位
    other_cols = [c for c in df.columns if c not in [col_link, col_date]]
    col_media = df[other_cols].apply(lambda x: x.astype(str).str.len().mean()).idxmin()
    col_title = df[other_cols].apply(lambda x: x.astype(str).str.len().mean()).idxmax()

    # 數據聚合
    df['title'] = df[col_title].astype(str).str.strip()
    df['link'] = df[col_link].astype(str).str.strip()
    df['media'] = df[col_media].astype(str).str.strip()
    df['date'] = df[col_date].astype(str).str.strip()

    grouped = df.groupby('title').agg({'link': list, 'media': list, 'date': 'max'}).reset_index()
    grouped['count'] = grouped['link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    for i, (_, row) in enumerate(grouped.iterrows()):
        with st.container():
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-text">#{i+1} RANKING</div>
                    <div class="topic-title">{row['title']}</div>
                    <div class="info-bar">📅 最新日期：{row['date']} ｜ 🔥 露出次數：{row['count']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with st.expander(f"📂 查看 {row['count']} 家媒體報導詳情"):
                for m, l in zip(row['media'], row['link']):
                    # 💡 這裡會顯示 n8n 寫入的真實媒體名稱
                    st.write(f"**[{m}]** ➔ [{row['title']}]({l})")

except Exception as e:
    st.error("資料解析中...")
