import streamlit as st
import pandas as pd

# 1. 頁面風格設定 (淺色溫和版)
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcf9; color: #37474f; }
    .news-card {
        background-color: #ffffff; padding: 28px; border-radius: 12px;
        border: 1px solid #f0f0ed; margin-bottom: 22px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }
    .main-title { text-align: center; color: #263238; font-weight: 800; font-size: 2.2em; margin-top: 20px; }
    .sub-title { text-align: center; color: #90a4ae; font-size: 0.95em; margin-bottom: 40px; }
    .rank-text { color: #af946d; font-weight: 900; font-size: 1.6em; margin-bottom: 10px; }
    .news-title { font-size: 1.4em; font-weight: 700; color: #2c3e50; margin: 10px 0; line-height: 1.5; }
    .source-container { margin-top: 20px; padding-top: 15px; border-top: 1px solid #f1f1f1; }
    .source-btn {
        display: inline-block; background-color: #f4f6f7; color: #566573 !important;
        padding: 7px 16px; border-radius: 6px; font-size: 0.85em;
        margin: 5px; border: 1px solid #d5dbdb; text-decoration: none; 
    }
    .info-label { color: #95a5a6; font-size: 0.85em; font-weight: 600; margin-right: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-title'>📡 資策會輿情熱度觀測站</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>WEEKLY TRENDING REPORT</div>", unsafe_allow_html=True)

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python')
    
    # 鎖定欄位：第2欄(索引1)是日期，第3欄(索引2)是標題，第4欄(索引3)是連結
    df['date'] = df.iloc[:, 1].fillna("近期").astype(str).str.strip()
    df['title'] = df.iloc[:, 2].fillna("未知標題").astype(str).str.replace(r'\n', '', regex=True).str.strip()
    df['link'] = df.iloc[:, 3].fillna("").astype(str).str.strip()

    df = df[df['title'].str.len() > 2] 
    df = df[~df['title'].str.contains("新聞標題")]

    # 聚合：同時保留最新的日期與所有連結
    grouped = df.groupby('title').agg({'link': list, 'date': 'max'}).reset_index()
    grouped['count'] = grouped['link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    for i, (_, row) in enumerate(grouped.iterrows()):
        title = row['title']
        links = row['link']
        count = row['count']
        latest_date = row['date']
        
        medal = "🥇 CHAMPION" if i == 0 else "🥈 SILVER" if i == 1 else "🥉 BRONZE" if i == 2 else f"TOP {i+1}"
        links_html = "".join([f'<a class="source-btn" href="{u}" target="_blank">來源 {idx+1}</a>' for idx, u in enumerate(links) if 'http' in str(u)])
        
        st.markdown(f"""
            <div class="news-card">
                <div class="rank-text">{medal}</div>
                <div class="news-title">{title}</div>
                <div style="margin-bottom: 15px;">
                    <span class="info-label">📅 最新日期：{latest_date}</span>
                    <span class="info-label">📈 本週熱度：{count} 次報導</span>
                </div>
                <div class="source-container">
                    <div style="color: #bdc3c7; font-size: 0.8em; margin-bottom: 10px;">🔗 相關報導連結：</div>
                    {links_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"系統資料校準中。")
