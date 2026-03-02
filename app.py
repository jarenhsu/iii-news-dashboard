import streamlit as st
import pandas as pd

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

try:
    # 讀取資料
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("媒體報導")

    # 🧠 內容特徵過濾邏輯
    # 1. 找連結欄 (含 http)
    col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), None)
    
    # 2. 找日期欄 (排除 Timestamp，找格式為 YYYY-MM-DD 的那一欄)
    # 我們排除掉包含「下午」或「上午」字眼的欄位，那是 Timestamp
    possible_date_cols = [c for c in df.columns if not df[c].astype(str).str.contains('午').any()]
    col_date = next((c for c in possible_date_cols if df[c].astype(str).str.match(r'\d{4}').any()), None)

    # 3. 找媒體名稱欄 (排除連結、日期、Timestamp 後，字數最短的那一欄)
    remaining_cols = [c for c in df.columns if c != col_link and c != col_date and not df[c].astype(str).str.contains('午').any()]
    # 過濾掉「新聞標題」這種長標題
    potential_media = [c for c in remaining_cols if df[c].astype(str).str.len().mean() < 15]
    col_media = potential_media[0] if potential_media else None

    # 4. 找標題欄 (剩餘中最長的那一欄)
    col_title = next((c for c in remaining_cols if c != col_media), df.columns[2])

    # 數據清洗
    df['title'] = df[col_title].astype(str).str.strip()
    df['link'] = df[col_link].astype(str).str.strip()
    df['media'] = df[col_media].astype(str).str.strip() if col_media else "媒體報導"
    df['date'] = df[col_date].astype(str).str.strip() if col_date else "近期"

    # 排除雜訊
    df = df[df['title'].str.len() > 5]
    df = df[~df['title'].str.contains("標題|Timestamp")]

    # 聚合
    grouped = df.groupby('title').agg({'link': list, 'media': list, 'date': 'max'}).reset_index()
    grouped['count'] = grouped['link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    for i, (_, row) in enumerate(grouped.iterrows()):
        st.markdown(f"""<div class="news-card">
            <div class="rank-text">RANK #{i+1}</div>
            <div class="topic-title">{row['title']}</div>
            <div class="info-bar">📅 最新日期：{row['date']} ｜ 🔥 熱度：{row['count']} 次露出</div>
        </div>""", unsafe_allow_html=True)
        
        with st.expander(f"📂 查看詳細媒體來源清單"):
            for m, l in zip(row['media'], row['link']):
                # 💡 如果 m 還是抓到時間，這裡會強制顯示為「媒體報導」
                display_media = "媒體報導" if "午" in str(m) or "/" in str(m) else m
                st.write(f"**[{display_media}]** ➔ [閱讀原文]({l})")

except Exception as e:
    st.error("資料校準中...")
