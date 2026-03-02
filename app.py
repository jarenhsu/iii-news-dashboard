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

    # 🧠 強化型欄位特徵辨識
    # 1. 找連結：含 http
    col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), None)
    
    # 2. 找日期：格式為 YYYY-MM-DD (例如 2026-03-02)
    col_date = next((c for c in df.columns if df[c].astype(str).str.match(r'\d{4}-\d{2}-\d{2}').any()), None)
    
    # 3. 找媒體名稱：排除連結、日期，且「不含」時間特徵 (/, :, 上午, 下午)
    def is_timestamp(val):
        s = str(val)
        return any(x in s for x in ['/', ':', '上午', '下午'])

    other_cols = [c for c in df.columns if c != col_link and c != col_date]
    # 在剩下的欄位中，找出一欄「平均字數最短」且「不是時間」的
    potential_media_cols = [c for c in other_cols if not df[c].apply(is_timestamp).any()]
    
    if potential_media_cols:
        col_media = df[potential_media_cols].apply(lambda x: x.astype(str).str.len().mean()).idxmin()
        col_title = df[potential_media_cols].apply(lambda x: x.astype(str).str.len().mean()).idxmax()
    else:
        # 萬一真的找不到，就設為預設
        col_media = None
        col_title = next((c for c in other_cols), df.columns[2])

    # 數據清洗
    df['title'] = df[col_title].astype(str).str.strip()
    df['link'] = df[col_link].astype(str).str.strip() if col_link else ""
    df['media'] = df[col_media].astype(str).str.strip() if col_media else "媒體報導"
    df['date'] = df[col_date].astype(str).str.strip() if col_date else "近期"

    # 排除雜訊
    df = df[df['title'].str.len() > 5]
    df = df[~df['title'].str.contains("標題|Timestamp")]

    # 聚合
    grouped = df.groupby('title').agg({'link': list, 'media': list, 'date': 'max'}).reset_index()
    grouped['count'] = grouped['link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    for i, (_, row) in enumerate(grouped.iterrows()):
        st.markdown(f"""
            <div class="news-card">
                <div class="rank-text">RANK #{i+1}</div>
                <div class="topic-title">{row['title']}</div>
                <div class="info-bar">📅 最新日期：{row['date']} ｜ 🔥 熱度：{row['count']} 次露出</div>
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander(f"📂 查看詳細媒體來源清單"):
            for m, l in zip(row['media'], row['link']):
                # 最終保險：如果內容還是長得像時間，就顯示媒體報導
                display_m = "媒體報導" if is_timestamp(m) else m
                st.write(f"**[{display_m}]** ➔ [閱讀原文]({l})")

except Exception as e:
    st.error(f"資料校準中...")
