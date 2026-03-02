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
    .info-bar { margin-bottom: 15px; font-size: 0.85em; color: #95a5a6; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-title'>📡 資策會輿情熱度觀測站</div>", unsafe_allow_html=True)

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取資料
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")

    # 💡 智慧對位邏輯：直接從所有欄位中搜尋關鍵內容
    # 1. 找連結：內容包含 http
    col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), None)
    # 2. 找日期：內容包含 2026 或 2025 (或符合日期格式)
    col_date = next((c for c in df.columns if df[c].astype(str).str.contains('202').any()), None)
    # 3. 找媒體：排除連結與日期後，字數較短的欄位 (例如: 聯合報、MSN)
    other_cols = [c for c in df.columns if c not in [col_link, col_date]]
    col_media = df[other_cols].apply(lambda x: x.astype(str).str.len().mean()).idxmin()
    # 4. 找標題：剩餘欄位中字數最長的那一欄
    col_title = df[other_cols].apply(lambda x: x.astype(str).str.len().mean()).idxmax()

    # 數據聚合
    df['title'] = df[col_title].astype(str).str.replace(r'\n', '', regex=True).str.strip()
    df['link'] = df[col_link].astype(str).str.strip()
    df['media'] = df[col_media].astype(str).str.strip()
    df['date'] = df[col_date].astype(str).str.strip()

    # 排除標頭雜訊
    df = df[df['title'].str.len() > 5]
    df = df[~df['title'].str.contains("標題")]

    # 依標題分組
    grouped = df.groupby('title').agg({'link': list, 'media': list, 'date': 'max'}).reset_index()
    grouped['count'] = grouped['link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    if grouped.empty:
        st.info("💡 目前資料同步中，請手動執行 n8n 流程。")
    else:
        for i, (_, row) in enumerate(grouped.iterrows()):
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-text">TOP {i+1} RANKING</div>
                    <div class="topic-title">{row['title']}</div>
                    <div class="info-bar">📅 最新日期：{row['date']} ｜ 🔥 累計露出：{row['count']} 次</div>
                </div>
                """, unsafe_allow_html=True)
            
            with st.expander(f"📂 查看 {row['count']} 家媒體報導詳情"):
                # 將媒體與連結配對，並過濾重複
                for m, l in zip(row['media'], row['link']):
                    st.write(f"**[{m}]** ➔ [閱讀原文]({l})")

except Exception as e:
    # 如果還是失敗，顯示具體哪一欄出錯
    st.error(f"❌ 偵測到欄位格式異常。")
    st.write("建議檢查 Google 試算表是否已發佈，且資料已由 n8n 正確寫入。")
