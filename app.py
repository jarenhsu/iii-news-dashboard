import streamlit as st
import pandas as pd

# 1. 頁面風格設定 (淺色溫和質感)
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
    .topic-title { font-size: 1.4em; font-weight: 700; color: #2c3e50; margin-bottom: 15px; line-height: 1.4; }
    .info-bar { margin-bottom: 15px; font-size: 0.85em; color: #95a5a6; display: flex; gap: 15px; }
    .stExpander { border: none !important; background-color: #f8f9fa !important; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-title'>📡 資策會輿情熱度觀測站</div>", unsafe_allow_html=True)

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("未知")

    # --- 智慧對位欄位 ---
    col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), df.columns[3])
    col_date = next((c for c in df.columns if df[c].astype(str).str.match(r'\d{4}-\d{2}-\d{2}').any()), df.columns[1])
    
    # 尋找媒體名稱欄：字數通常較短
    other_cols = [c for c in df.columns if c not in [col_link, col_date]]
    col_media = df[other_cols].apply(lambda x: x.astype(str).str.len().mean()).idxmin()
    col_title = df[other_cols].apply(lambda x: x.astype(str).str.len().mean()).idxmax()

    # 清洗與轉換
    df['c_title'] = df[col_title].astype(str).str.replace(r'\n', '', regex=True).str.strip()
    df['c_date'] = df[col_date].astype(str).str.strip()
    df['c_link'] = df[col_link].astype(str).str.strip()
    df['c_media'] = df[col_media].astype(str).str.strip()

    # 聚合資料：依標題分組
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
                <div class="rank-text">RANK #{i+1}</div>
                <div class="topic-title">{row['c_title']}</div>
                <div class="info-bar">
                    <span>📅 最新日期：{row['c_date']}</span>
                    <span>🔥 本週累計：{row['count']} 次媒體露出</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander(f"📂 查看 {row['count']} 家媒體報導詳情清單"):
            for m, l in zip(row['c_media'], row['c_link']):
                # 這裡會顯示 n8n 抓到的真實媒體名稱
                st.markdown(f"**[{m}]** ➔ [閱讀原文]({l})")

except Exception as e:
    st.error("資料解析校準中，請確認 n8n 已完成媒體名稱與日期寫入。")
