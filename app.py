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
    # 讀取並跳過可能有問題的行
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("未提供")

    # 💡 關鍵修正：強制指定欄位索引，避免所有標題都變成一樣的
    # 假設順序：[0]時間戳記, [1]日期, [2]標題, [3]連結, [4]媒體
    if df.shape[1] >= 5:
        df['c_date'] = df.iloc[:, 1].astype(str).str.strip()
        df['c_title'] = df.iloc[:, 2].astype(str).str.replace(r'\n', '', regex=True).str.strip()
        df['c_link'] = df.iloc[:, 3].astype(str).str.strip()
        df['c_media'] = df.iloc[:, 4].astype(str).str.strip()
    else:
        # 如果欄位不足，嘗試自動偵測
        df['c_title'] = df.iloc[:, 1].astype(str) # 預防性指定
        df['c_link'] = df.iloc[:, -1].astype(str)
        df['c_date'] = "近期"
        df['c_media'] = "媒體報導"

    # 排除無效資料（例如標頭或太短的字）
    df = df[df['c_title'].str.len() > 5]
    df = df[~df['c_title'].str.contains("標題|Timestamp")]

    # 聚合：依照「標題」分組
    # 如果這裡「每個新聞都一樣」，代表 df['c_title'] 的內容在試算表裡真的都一樣
    grouped = df.groupby('c_title').agg({
        'c_link': list, 
        'c_media': list, 
        'c_date': 'max'
    }).reset_index()
    
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    if grouped.empty:
        st.warning("目前沒有符合條件的新聞資料，請檢查試算表內容。")
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
            
            with st.expander(f"📂 查看 {row['count']} 家媒體來源詳情"):
                # 這裡使用 zip 同時取出媒體與連結
                for m, l in zip(row['c_media'], row['c_link']):
                    st.write(f"**[{m}]** ➔ [點此閱讀原文]({l})")

except Exception as e:
    st.error(f"資料對位異常：{e}")
