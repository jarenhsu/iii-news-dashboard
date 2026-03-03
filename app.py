import streamlit as st
import pandas as pd
from urllib.parse import urlparse

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

def get_media_name(url, raw_media):
    # 優先使用試算表抓到的名稱，排除時間格式
    clean_m = str(raw_media).strip()
    if len(clean_m) > 1 and "午" not in clean_m and "媒體" not in clean_m and "/" not in clean_m:
        return clean_m
    
    # 網址解析保險機制
    mapping = {
        "yahoo": "Yahoo新聞", "udn": "聯合新聞網", "ltn": "自由時報", "chinatimes": "中時新聞網",
        "ettoday": "ETtoday", "storm": "風傳媒", "cna": "中央社", "setn": "三立新聞",
        "tvbs": "TVBS", "find.org.tw": "FIND中心", "iii.org.tw": "資策會官網"
    }
    domain = urlparse(str(url)).netloc.lower()
    for key, name in mapping.items():
        if key in domain: return name
    return domain.split('.')[-2].upper() if '.' in domain else "媒體報導"

try:
    # 讀取資料
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")

    # 💡 依照你確認的「第 6 欄」進行強制對位 (索引從 0 開始，所以第 6 欄是 5)
    if df.shape[1] >= 6:
        df['c_date'] = df.iloc[:, 1].astype(str).str.strip()
        df['c_title'] = df.iloc[:, 2].astype(str).str.replace(r'\n', '', regex=True).str.strip()
        df['c_link'] = df.iloc[:, 3].astype(str).str.strip()
        df['raw_media'] = df.iloc[:, 5].astype(str).str.strip() # 強制抓取第 6 欄 (F)
    else:
        # 欄位不足時的後備方案
        df['c_date'] = df.iloc[:, 1]
        df['c_title'] = df.iloc[:, 2]
        df['c_link'] = df.iloc[:, 3]
        df['raw_media'] = ""

    # 排除雜訊
    df = df[df['c_title'].str.len() > 5]
    df = df[~df['c_title'].str.contains("標題|Timestamp")]

    # 聚合：依標題分組
    grouped = df.groupby('c_title').agg({'c_link': list, 'raw_media': list, 'c_date': 'max'}).reset_index()
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    if grouped.empty:
        st.warning("⚠️ 資料解析中，請確認試算表 C 欄有正確標題。")
    else:
        for i, (_, row) in enumerate(grouped.iterrows()):
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-text">RANK #{i+1}</div>
                    <div class="topic-title">{row['c_title']}</div>
                    <div class="info-bar">
                        <span>📅 最新日期：{row['c_date']}</span>
                        <span>🔥 熱度：{row['count']} 次報導</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with st.expander(f"📂 查看詳細媒體來源"):
                for link, raw_m in zip(row['c_link'], row['raw_media']):
                    m_name = get_media_name(link, raw_m)
                    st.write(f"**[{m_name}]** ➔ [閱讀原文]({link})")

except Exception as e:
    st.error(f"⚠️ 讀取失敗，原因：{e}")
