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

def get_media_label(url, raw_m):
    clean_m = str(raw_m).strip()
    if len(clean_m) > 1 and not any(x in clean_m for x in ['/', ':', '午']):
        return clean_m
    mapping = {"yahoo": "Yahoo新聞", "udn": "聯合新聞網", "ltn": "自由時報", "chinatimes": "中時新聞網", "ettoday": "ETtoday", "storm": "風傳媒"}
    domain = urlparse(str(url)).netloc.lower()
    for k, v in mapping.items():
        if k in domain: return v
    return domain.split('.')[-2].upper() if '.' in domain else "媒體報導"

try:
    # 讀取資料
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")

    # 💡 智慧掃描：找出哪一欄才是真的標題
    # 排除掉包含 http (連結) 與 包含 "/" (時間) 的欄位
    potential_cols = [c for c in df.columns if not df[c].astype(str).str.contains('http|/|:').any()]
    
    # 在剩下的欄位中，平均字數最長的那一欄就是「新聞標題」
    col_title = df[potential_cols].apply(lambda x: x.astype(str).str.len().mean()).idxmax()
    
    # 連結欄
    col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), df.columns[3])
    
    # 媒體欄 (假設在最後一欄)
    col_media = df.columns[5] if df.shape[1] >= 6 else df.columns[-1]

    df['c_title'] = df[col_title].astype(str).str.strip()
    df['c_link'] = df[col_link].astype(str).str.strip()
    df['raw_media'] = df[col_media].astype(str).str.strip()

    # 極簡過濾：只要標題長度大於 2 就留著
    df = df[df['c_title'].str.len() > 2]
    df = df[~df['c_title'].str.contains("標題|Timestamp")]

    # 聚合
    grouped = df.groupby('c_title').agg({'c_link': list, 'raw_media': list}).reset_index()
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    if grouped.empty:
        st.warning("⚠️ 試算表內尚無有效新聞標題，請檢查 n8n 是否成功寫入 C 欄。")
    else:
        for i, (_, row) in enumerate(grouped.iterrows()):
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-text">RANK #{i+1}</div>
                    <div class="topic-title">{row['c_title']}</div>
                    <div class="info-bar">🔥 輿情熱度：{row['count']} 次媒體報導</div>
                </div>
                """, unsafe_allow_html=True)
            
            with st.expander(f"📂 查看詳細來源"):
                for l, rm in zip(row['c_link'], row['raw_media']):
                    st.write(f"**[{get_media_label(l, rm)}]** ➔ [閱讀原文]({l})")

except Exception as e:
    st.error(f"解析失敗：{e}")
