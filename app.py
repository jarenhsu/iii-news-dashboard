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
    .main-title { text-align: center; color: #263238; font-weight: 800; font-size: 2.2em; margin-top: 10px; }
    .sub-title { text-align: center; color: #90a4ae; font-size: 1em; margin-bottom: 30px; }
    .rank-text { color: #af946d; font-weight: 900; font-size: 1.5em; margin-bottom: 5px; }
    .topic-title { font-size: 1.4em; font-weight: 700; color: #2c3e50; margin-bottom: 15px; line-height: 1.4; }
    .info-bar { margin-bottom: 15px; font-size: 0.85em; color: #95a5a6; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-title'>📡 資策會輿情熱度觀測站</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>媒體露出 > 標題清單分析儀表板</div>", unsafe_allow_html=True)

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python')
    
    # 💡 強制按索引讀取：日期(1), 標題(2), 連結(3), 媒體名稱(4)
    df['c_date'] = df.iloc[:, 1].fillna("近期").astype(str).str.strip()
    df['c_title'] = df.iloc[:, 2].fillna("未知標題").astype(str).str.replace(r'\n', '', regex=True).str.strip()
    df['c_link'] = df.iloc[:, 3].fillna("").astype(str).str.strip()
    df['c_media'] = df.iloc[:, 4].fillna("媒體報導").astype(str).str.strip()

    df = df[df['c_title'].str.len() > 2]
    df = df[~df['c_title'].str.contains("新聞標題")]

    # 聚合：保留媒體清單與連結清單
    grouped = df.groupby('c_title').agg({
        'c_link': list, 
        'c_media': list, 
        'c_date': 'max'
    }).reset_index()
    
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    for i, (_, row) in enumerate(grouped.iterrows()):
        title = row['c_title']
        links = row['c_link']
        medias = row['c_media']
        latest_date = row['c_date']
        count = row['count']
        
        medal = "🥇 CHAMPION" if i == 0 else "🥈 SILVER" if i == 1 else "🥉 BRONZE" if i == 2 else f"TOP {i+1}"
        
        st.markdown(f"""
            <div class="news-card">
                <div class="rank-text">{medal}</div>
                <div class="topic-title">{title}</div>
                <div class="info-bar">📅 最新日期：{latest_date} ｜ 🔥 本週累計：{count} 次媒體露出</div>
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander(f"📂 點擊查看共 {count} 家媒體報導列表"):
            for link, m_name in zip(links, medias):
                # 💡 這裡會顯示 n8n 抓到的真實媒體名稱
                st.markdown(f"**[{m_name}]** ➔ [{title}]({link})")

except Exception as e:
    st.error(f"資料同步中，請確認試算表格式。")
