import streamlit as st
import pandas as pd

st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

# 保持淺色溫和風格
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
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("媒體報導")

    # 💡 智慧對位：優先找包含關鍵字的欄位
    col_date = next((c for c in df.columns if '日期' in str(c) or 'Date' in str(c)), df.columns[1])
    col_title = next((c for c in df.columns if '標題' in str(c) or 'Title' in str(c)), df.columns[2])
    col_link = next((c for c in df.columns if '連結' in str(c) or 'http' in str(df[c].iloc[0] if len(df)>0 else "")), df.columns[3])
    col_media = next((c for c in df.columns if '媒體' in str(c) or 'Source' in str(c)), df.columns[-1])

    df['c_title'] = df[col_title].astype(str).str.strip()
    df['c_link'] = df[col_link].astype(str).str.strip()
    df['c_date'] = df[col_date].astype(str).str.strip()
    df['c_media'] = df[col_media].astype(str).str.strip()

    # 聚合
    grouped = df.groupby('c_title').agg({'c_link': list, 'c_media': list, 'c_date': 'max'}).reset_index()
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    for i, (_, row) in enumerate(grouped.iterrows()):
        st.markdown(f"""<div class="news-card">
            <div class="rank-text">RANK #{i+1}</div>
            <div class="topic-title">{row['c_title']}</div>
            <div class="info-bar">📅 日期：{row['c_date']} ｜ 🔥 熱度：{row['count']} 次報導</div>
        </div>""", unsafe_allow_html=True)
        
        with st.expander(f"📂 查看 {row['count']} 家媒體來源清單"):
            for m, l in zip(row['c_media'], row['c_link']):
                st.write(f"**[{m}]** ➔ [閱讀原文]({l})")

except Exception as e:
    st.error(f"資料校準中，請手動執行 n8n 寫入媒體欄位。")
