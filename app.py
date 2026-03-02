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
    # 讀取資料並跳過雜訊
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python')
    
    # 💡 強制過濾掉包含「未提供」、「標題」或空值的無效列
    df = df.dropna(how='all')

    # 智慧識別欄位 (透過內容特徵)
    # 連結：找 http
    col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), None)
    # 日期：找 YYYY-MM-DD
    col_date = next((c for c in df.columns if df[c].astype(str).str.match(r'\d{4}-\d{2}-\d{2}').any()), None)
    
    # 排除日期與連結後的欄位
    other_cols = [c for c in df.columns if c not in [col_link, col_date]]
    # 標題：內容最長的一欄
    col_title = df[other_cols].apply(lambda x: x.astype(str).str.len().mean()).idxmax()
    # 媒體：剩餘欄位中較短的那一欄
    remaining = [c for c in other_cols if c != col_title]
    col_media = remaining[0] if remaining else None

    # 清洗與對位
    df['c_title'] = df[col_title].astype(str).str.strip()
    df['c_link'] = df[col_link].astype(str).str.strip() if col_link else ""
    df['c_date'] = df[col_date].astype(str).str.strip() if col_date else "近期"
    df['c_media'] = df[col_media].astype(str).str.strip() if col_media else "媒體報導"

    # 二次過濾：確保標題不是「未提供」
    df = df[~df['c_title'].str.contains("未提供|未知|新聞標題|Timestamp")]
    df = df[df['c_title'].str.len() > 5]

    # 聚合與排序
    grouped = df.groupby('c_title').agg({'c_link': list, 'c_media': list, 'c_date': 'max'}).reset_index()
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    if grouped.empty:
        st.warning("⚠️ 資料解析中，請手動執行 n8n 寫入正確的新聞標題。")
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
            
            with st.expander(f"📂 查看詳細媒體來源清單"):
                for m, l in zip(row['c_media'], row['c_link']):
                    st.write(f"**[{m}]** ➔ [閱讀原文]({l})")

except Exception as e:
    st.error("系統正在重新校準資料欄位，請稍候。")
