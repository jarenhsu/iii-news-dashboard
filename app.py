import streamlit as st
import pandas as pd

# 1. 頁面風格與樣式設定
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
    # 2. 讀取試算表資料
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")

    # 💡 根據最新試算表結構進行精準對位：
    # A(0):時間戳記 | B(1):新聞標題 | C(2):發布日期 | D(3):新聞連結 | E(4):所屬部門 | F(5):媒體
    df['title'] = df.iloc[:, 1].astype(str).str.strip()
    df['date'] = df.iloc[:, 2].astype(str).str.strip()
    df['link'] = df.iloc[:, 3].astype(str).str.strip()
    df['media'] = df.iloc[:, 5].astype(str).str.strip() # 強制抓取 F 欄媒體名稱

    # 3. 數據清洗：移除系統雜訊與無效標題
    df = df[df['title'].str.len() > 5]
    df = df[~df['title'].str.contains("解析失敗|提取中|未知標題|新聞標題")]

    # 4. 數據聚合：依據標題分組並計算露出熱度
    grouped = df.groupby('title').agg({
        'link': list, 
        'media': list, 
        'date': 'max'
    }).reset_index()

    grouped['count'] = grouped['link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    # 5. 渲染觀測站卡片
    if grouped.empty:
        st.info("💡 資料同步中，請確保 n8n 已成功寫入新聞至試算表。")
    else:
        for i, (_, row) in enumerate(grouped.iterrows()):
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-text">TOP {i+1}</div>
                    <div class="topic-title">{row['title']}</div>
                    <div class="info-bar">
                        <span>🔥 {row['count']} 次露出</span>
                        <span>📅 最新日期：{row['date'] if len(row['date']) > 1 else '近期'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with st.expander(f"📂 查看詳細來源細節"):
                # 排除重複出現的連結
                unique_sources = []
                seen_links = set()
                for m, l in zip(row['media'], row['link']):
                    if l not in seen_links:
                        unique_sources.append((m, l))
                        seen_links.add(l)
                
                for m, l in unique_sources:
                    # 如果試算表沒抓到媒體名，顯示「相關媒體」補位
                    display_m = m if len(m) > 1 else "相關媒體"
                    st.write(f"**[{display_m}]** ➔ [閱讀原文]({l})")

except Exception as e:
    st.error(f"⚠️ 解析異常：{e}")
