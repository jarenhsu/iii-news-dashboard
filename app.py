import streamlit as st
import pandas as pd
from urllib.parse import urlparse

# 1. 頁面風格
st.set_page_config(page_title="資策會輿情熱度觀測站", layout="centered")
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
    # 2. 讀取資料
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")

    # 💡 根據最新試算表：
    # A(0):時間 | B(1):標題 | C(2):日期 | D(3):連結 | E(4):部門 | F(5):媒體
    df['c_title'] = df.iloc[:, 1].astype(str).str.strip()
    df['c_date'] = df.iloc[:, 2].astype(str).str.strip()
    df['c_link'] = df.iloc[:, 3].astype(str).str.strip()
    # 關鍵：強制指定 F 欄 (索引 5) 為媒體名稱
    df['c_media'] = df.iloc[:, 5].astype(str).str.strip()

    # 過濾雜訊：排除標題太短或系統預設詞
    df = df[df['c_title'].str.len() > 5]
    df = df[~df['c_title'].str.contains("解析失敗|提取中|未知標題|新聞標題")]

    # 3. 數據聚合
    grouped = df.groupby('c_title').agg({'c_link': list, 'c_media': list, 'c_date': 'max'}).reset_index()
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    if grouped.empty:
        st.info("💡 資料同步中...")
    else:
        for i, (_, row) in enumerate(grouped.iterrows()):
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-text">TOP {i+1}</div>
                    <div class="topic-title">{row['c_title']}</div>
                    <div class="info-bar">
                        <span>🔥 {row['count']} 次露出</span>
                        <span>📅 最新日期：{row['c_date']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with st.expander(f"📂 查看詳細來源細節"):
                # 排除重複連結
                unique_sources = []
                seen_links = set()
                for m, l in zip(row['c_media'], row['c_link']):
                    if l not in seen_links:
                        unique_sources.append((m, l))
                        seen_links.add(l)
                
                for m, l in unique_sources:
                    # 💡 邏輯：優先顯示試算表媒體名，若為空則解析網址
                    if len(m) > 1 and not m.startswith("http"):
                        display_name = m
                    else:
                        domain = urlparse(l).netloc.replace("www.", "").split('.')[0].upper()
                        display_name = domain if domain else "相關媒體"
                    
                    st.write(f"**[{display_name}]** ➔ [閱讀原文]({l})")

except Exception as e:
    st.error(f"解析發生錯誤：{e}")
