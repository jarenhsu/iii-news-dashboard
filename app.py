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

# 2. 數據獲取
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取 CSV 資料
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("未提供")

    # 💡 關鍵修正：直接依照你試算表的欄位位置抓取
    # 假設：B欄是日期(1), C欄是標題(2), D欄是連結(3), E欄是媒體(4)
    if df.shape[1] >= 4:
        df['c_date'] = df.iloc[:, 1].astype(str).str.strip()
        df['c_title'] = df.iloc[:, 2].astype(str).str.replace(r'\n', '', regex=True).str.strip()
        df['c_link'] = df.iloc[:, 3].astype(str).str.strip()
        # 如果有第五欄就抓媒體，沒有就補「媒體報導」
        df['c_media'] = df.iloc[:, 4].astype(str).str.strip() if df.shape[1] >= 5 else "媒體報導"
    else:
        st.error("試算表欄位不足，請確認 n8n 是否成功寫入日期、標題與連結。")
        st.stop()

    # 💡 這次放寬過濾：只要標題長度大於 2 就顯示
    df = df[df['c_title'].str.len() > 2]
    df = df[~df['c_title'].str.contains("新聞標題|Timestamp|標題")]

    # 聚合：依照「標題」分組
    grouped = df.groupby('c_title').agg({
        'c_link': list, 
        'c_media': list, 
        'c_date': 'max'
    }).reset_index()
    
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(20)

    if grouped.empty:
        st.warning("⚠️ 目前讀取到的標題過短或格式不符，請檢查試算表 C 欄內容。")
    else:
        for i, (_, row) in enumerate(grouped.iterrows()):
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-text">RANK #{i+1}</div>
                    <div class="topic-title">{row['c_title']}</div>
                    <div class="info-bar">
                        <span>📅 日期：{row['c_date']}</span>
                        <span>🔥 熱度：{row['count']} 次露出</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with st.expander(f"📂 查看媒體來源詳情"):
                # 配對顯示
                for m, l in zip(row['c_media'], row['c_link']):
                    st.write(f"**[{m}]** ➔ [點此閱讀原文]({l})")

except Exception as e:
    st.error(f"系統偵測到錯誤：{e}")
