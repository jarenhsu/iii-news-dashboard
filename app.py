import streamlit as st
import pandas as pd

# 1. 頁面風格設定 (淺色溫和質感)
st.set_page_config(page_title="資策會輿情熱度觀測站", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcf9; color: #37474f; }
    .news-card {
        background-color: #ffffff; padding: 25px; border-radius: 12px;
        border: 1px solid #f0f0ed; margin-bottom: 25px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }
    .main-title { text-align: center; color: #263238; font-weight: 800; font-size: 2.2em; margin-top: 10px; }
    .sub-title { text-align: center; color: #90a4ae; font-size: 1em; margin-bottom: 30px; }
    .rank-text { color: #af946d; font-weight: 900; font-size: 1.5em; margin-bottom: 5px; }
    .topic-title { font-size: 1.4em; font-weight: 700; color: #2c3e50; margin-bottom: 15px; line-height: 1.4; }
    .info-bar { margin-bottom: 15px; font-size: 0.85em; color: #95a5a6; display: flex; gap: 15px; flex-wrap: wrap; }
    .stExpander { border: none !important; background-color: #f8f9fa !important; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-title'>📡 資策會輿情熱度觀測站</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>WEEKLY TRENDING REPORT</div>", unsafe_allow_html=True)

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")

    # --- 🧠 終極特徵對位邏輯 ---
    # 1. 找連結欄 (內容包含 http)
    col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), None)
    
    # 2. 找日期欄 (內容長度通常是 10 且包含 "-"，例如 2026-03-02)
    col_date = next((c for c in df.columns if df[c].astype(str).str.match(r'\d{4}-\d{2}-\d{2}').any()), None)
    
    # 3. 找媒體欄 (排除連結和日期後，字數較短的欄位，或標題含「媒體」)
    possible_media_cols = [c for c in df.columns if c not in [col_link, col_date] and '標題' not in str(c)]
    col_media = next((c for c in possible_media_cols if '媒體' in str(c)), None)
    if not col_media and possible_media_cols:
        col_media = df[possible_media_cols].apply(lambda x: x.astype(str).str.len().mean()).idxmin()

    # 4. 找標題欄 (剩餘欄位中，平均字數最長的那一欄)
    remaining_cols = [c for c in df.columns if c not in [col_link, col_date, col_media]]
    col_title = df[remaining_cols].apply(lambda x: x.astype(str).str.len().mean()).idxmax()

    # --- 數據清洗 ---
    df['c_title'] = df[col_title].astype(str).str.replace(r'\n', '', regex=True).str.strip()
    df['c_link'] = df[col_link].astype(str).str.strip() if col_link else ""
    df['c_date'] = df[col_date].astype(str).str.strip() if col_date else "近期"
    df['c_media'] = df[col_media].astype(str).str.strip() if col_media else "媒體報導"

    # 排除標頭雜訊
    df = df[df['c_title'].str.len() > 2]
    df = df[~df['c_title'].str.contains("新聞標題|標題")]

    # 聚合資料
    grouped = df.groupby('c_title').agg({
        'c_link': list, 
        'c_media': list, 
        'c_date': 'max'
    }).reset_index()
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    # --- 顯示卡片 ---
    for i, (_, row) in enumerate(grouped.iterrows()):
        title = row['c_title']
        links = row['c_link']
        medias = row['c_media']
        date = row['c_date']
        count = row['count']
        
        medal = "🥇 CHAMPION" if i == 0 else "🥈 SILVER" if i == 1 else "🥉 BRONZE" if i == 2 else f"TOP {i+1}"
        
        st.markdown(f"""
            <div class="news-card">
                <div class="rank-text">{medal}</div>
                <div class="topic-title">{title}</div>
                <div class="info-bar">
                    <span>📅 最新日期：{date}</span>
                    <span>🔥 本週累計：{count} 次媒體露出</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander(f"📂 點擊查看共 {count} 家媒體報導列表"):
            for l, m in zip(links, medias):
                st.markdown(f"**[{m}]** ➔ [{title}]({l})")

except Exception as e:
    st.error("資料解析校準中，請稍候重新整理。")
