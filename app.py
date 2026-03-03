import streamlit as st
import pandas as pd

# 1. 樣式設定
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
    .topic-title { font-size: 1.3em; font-weight: 700; color: #2c3e50; margin-bottom: 15px; }
    .info-bar { margin-bottom: 15px; font-size: 0.85em; color: #95a5a6; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center; padding:20px;'><h1 style='color:#263238;'>📡 資策會輿情熱度觀測站</h1></div>", unsafe_allow_html=True)

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")

    # 依照試算表位置對位
    df['c_title'] = df.iloc[:, 1].astype(str).str.strip()  # B 欄
    df['c_date'] = df.iloc[:, 2].astype(str).str.strip()   # C 欄
    df['c_link'] = df.iloc[:, 3].astype(str).str.strip()   # D 欄
    df['c_media'] = df.iloc[:, 5].astype(str).str.strip()  # F 欄

    # 排除雜訊資料
    df = df[df['c_title'].str.len() > 5]
    df = df[~df['c_title'].str.contains("提取中|解析失敗|媒體報導|Timestamp")]

    # 數據聚合
    grouped = df.groupby('c_title').agg({'c_link': list, 'c_media': list, 'c_date': 'max'}).reset_index()
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    if grouped.empty:
        st.info("💡 資料同步中，請確保 n8n 已成功寫入新聞標題至試算表。")
    else:
        for i, (_, row) in enumerate(grouped.iterrows()):
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-text">RANK #{i+1}</div>
                    <div class="topic-title">{row['c_title']}</div>
                    <div class="info-bar">📅 最新日期：{row['c_date']} ｜ 🔥 熱度：{row['count']} 次報導</div>
                </div>
                """, unsafe_allow_html=True)
            with st.expander("📂 查看媒體來源"):
                for m, l in zip(row['c_media'], row['c_link']):
                    st.write(f"**[{m if len(m)>1 else '相關媒體'}]** ➔ [閱讀原文]({l})")

# 💡 修正 SyntaxError 的關鍵區塊
except Exception as e:
    st.error(f"解析異常：{e}")
