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
    .topic-title { font-size: 1.3em; font-weight: 700; color: #2c3e50; margin-bottom: 15px; line-height: 1.5; }
    .info-bar { margin-bottom: 15px; font-size: 0.85em; color: #95a5a6; display: flex; gap: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center; padding:20px;'><h1 style='color:#263238;'>📡 資策會輿情熱度觀測站</h1></div>", unsafe_allow_html=True)

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("媒體報導")

    # 智慧識別欄位
    col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), None)
    col_date = next((c for c in df.columns if df[c].astype(str).str.match(r'\d{4}-\d{2}-\d{2}').any()), None)
    
    # 排除日期、連結與時間戳記 (含'午')，字數最長的是標題，最短的是媒體
    other_cols = [c for c in df.columns if c != col_link and c != col_date and not df[c].astype(str).str.contains('午').any()]
    
    if len(other_cols) >= 2:
        col_title = df[other_cols].apply(lambda x: x.astype(str).str.len().mean()).idxmax()
        col_media = df[other_cols].apply(lambda x: x.astype(str).str.len().mean()).idxmin()
    else:
        col_title = other_cols[0] if other_cols else df.columns[2]
        col_media = None

    df['title'] = df[col_title].astype(str).str.strip()
    df['link'] = df[col_link].astype(str).str.strip() if col_link else ""
    df['media'] = df[col_media].astype(str).str.strip() if col_media else "媒體報導"
    df['date'] = df[col_date].astype(str).str.strip() if col_date else "近期"

    # 排除標頭雜訊
    df = df[df['title'].str.len() > 5]
    df = df[~df['title'].str.contains("標題|Timestamp")]

    # 聚合：依標題分組
    grouped = df.groupby('title').agg({'link': list, 'media': list, 'date': 'max'}).reset_index()
    grouped['count'] = grouped['link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(20)

    for i, (_, row) in enumerate(grouped.iterrows()):
        st.markdown(f"""
            <div class="news-card">
                <div class="rank-text">RANK #{i+1}</div>
                <div class="topic-title">{row['title']}</div>
                <div class="info-bar">
                    <span>📅 最新日期：{row['date']}</span>
                    <span>🔥 熱度：{row['count']} 次報導</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander(f"📂 查看詳細媒體來源"):
            for m, l in zip(row['media'], row['link']):
                st.write(f"**[{m}]** ➔ [閱讀原文]({l})")

except Exception as e:
    st.error(f"⚠️ 讀取失敗：{e}")
    st.info("請確認 n8n 已寫入至少含有日期、標題、連結、媒體名稱的資料。")
