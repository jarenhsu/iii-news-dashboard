import streamlit as st
import pandas as pd
from urllib.parse import urlparse

# 1. 頁面風格設定
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e0e0e; color: #f0f0f0; }
    .news-card {
        background-color: #1a1a1a; padding: 30px; border-radius: 15px;
        border: 1px solid #333; margin-bottom: 25px; 
    }
    .main-title { text-align: center; color: #fff; font-weight: 900; font-size: 2.2em; margin-top: 20px; }
    .sub-title { text-align: center; color: #d4af37; font-size: 1em; margin-bottom: 40px; letter-spacing: 2px; }
    .rank-text { color: #d4af37; font-weight: 900; font-size: 1.8em; margin-bottom: 10px; }
    .news-title { font-size: 1.5em; font-weight: 700; color: #fff; margin: 10px 0; line-height: 1.4; }
    .source-container { margin-top: 20px; padding-top: 15px; border-top: 1px dashed #444; }
    .source-btn {
        display: inline-block; background-color: #2c2c2c; color: #d4af37 !important;
        padding: 6px 14px; border-radius: 20px; font-size: 0.85em;
        margin: 5px; border: 1px solid #d4af37; text-decoration: none;
    }
    .source-btn:hover { background-color: #d4af37; color: #000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 媒體名稱轉換加強版
def get_media_label(url):
    if not isinstance(url, str) or "google" in url: return "媒體報導"
    mapping = {
        "yahoo": "Yahoo新聞", "udn": "聯合新聞", "ltn": "自由時報", "chinatimes": "中時",
        "ettoday": "ETtoday", "storm": "風傳媒", "cna": "中央社", "setn": "三立新聞",
        "tvbs": "TVBS", "find.org.tw": "FIND中心", "iii.org.tw": "資策會官網"
    }
    domain = urlparse(url).netloc.lower()
    for key, name in mapping.items():
        if key in domain: return name
    return "相關報導"

st.markdown("<div class='main-title'>📡 資策會輿情熱度觀測站</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>WEEKLY TRENDING REPORT</div>", unsafe_allow_html=True)

# 2. 數據處理
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 💡 修正關鍵：強制跳過錯誤行，並指定欄位索引
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python')
    
    # 鎖定位置：第3欄(索引2)標題，第4欄(索引3)連結
    # 清洗掉標題內的換行符號 \n 以防分組失敗
    df['clean_title'] = df.iloc[:, 2].astype(str).str.replace(r'\n', '', regex=True).str.strip()
    df['clean_link'] = df.iloc[:, 3].astype(str).str.strip()

    # 過濾掉「新聞標題」這種標頭文字或空標題
    df = df[df['clean_title'] != '新聞標題']
    df = df[df['clean_title'] != 'nan']

    # 聚合資料
    grouped = df.groupby('clean_title')['clean_link'].apply(list).reset_index()
    grouped['count'] = grouped['clean_link'].apply(len)
    # 依熱度排序前 15 名
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    for i, (_, row) in enumerate(grouped.iterrows()):
        title = row['clean_title']
        links = row['clean_link']
        count = row['count']
        
        # 獎牌標籤
        medal = "🥇 CHAMPION" if i == 0 else "🥈 SILVER" if i == 1 else "🥉 BRONZE" if i == 2 else f"TOP {i+1}"
        
        # 生成連結按鈕
        links_html = "".join([f'<a class="source-btn" href="{u}" target="_blank">🌐 {get_media_label(u)}</a>' for u in links if u and 'http' in str(u)])
        
        # 顯示卡片
        st.markdown(f"""
            <div class="news-card">
                <div class="rank-text">{medal}</div>
                <div class="news-title">{title}</div>
                <div style="color: #d4af37; font-weight: bold; margin-bottom: 10px;">🔥 熱度：{count} 次報導</div>
                <div class="source-container">
                    <div style="color: #888; font-size: 0.8em; margin-bottom: 10px;">🔗 媒體來源：</div>
                    {links_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"資料校準中，請稍候。")
