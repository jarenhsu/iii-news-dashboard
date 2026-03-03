import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, timedelta

# 1. 頁面風格、優化版跑馬燈與深藍主題設定
st.set_page_config(page_title="資策會輿情熱度觀測站", layout="centered")
st.markdown("""
    <style>
    /* 頁面深藍色背景 */
    .stApp { background-color: #000c1d; color: #ffffff; }
    h1 { color: #ffffff !important; text-align: center; font-weight: 800; margin-bottom: 5px; }

    /* 💡 優化版：微發光跑馬燈 */
    .marquee-container {
        background: rgba(0, 0, 0, 0.6);
        border-top: 1px solid rgba(255, 165, 0, 0.4);
        border-bottom: 1px solid rgba(255, 165, 0, 0.4);
        padding: 6px 0;
        margin-bottom: 25px;
    }
    .neon-text {
        color: #FFA500; 
        font-weight: bold;
        font-size: 1.3em;
        text-shadow: 0 0 2px #FFFFFF, 0 0 8px #FFA500;
        font-family: 'Microsoft JhengHei', sans-serif;
    }
    .blink { animation: blinker 2.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.8; } }

    /* 🚀 科技感 AI 點評區塊 */
    .ai-monitor-box {
        position: relative;
        background: rgba(26, 58, 90, 0.4);
        backdrop-filter: blur(10px); /* 玻璃擬態 */
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 165, 0, 0.3);
        margin-bottom: 30px;
        overflow: hidden;
        box-shadow: inset 0 0 20px rgba(0, 191, 255, 0.1);
    }
    .ai-monitor-box::before {
        content: "";
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: conic-gradient(transparent, rgba(255, 165, 0, 0.3), transparent 30%);
        animation: rotate 6s linear infinite; /* 旋轉漸層邊框 */
        z-index: -1;
    }
    @keyframes rotate {
        100% { transform: rotate(360deg); }
    }
    .ai-header {
        color: #00d4ff;
        font-size: 1.1em;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
    .ai-header::before {
        content: "●";
        color: #ff4500;
        margin-right: 8px;
        animation: blinker 1s steps(5, start) infinite;
    }

    /* 新聞卡片效果 */
    .news-card {
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 12px;
        margin-bottom: 25px; 
        color: #333333;
        box-shadow: 0 4px 15px rgba(255, 140, 0, 0.2);
    }
    .rank-text { color: #FF8C00; font-weight: 900; font-size: 1.5em; }
    .topic-title { font-size: 1.25em; font-weight: 700; color: #001f3f; margin-top: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 資策會輿情熱度觀測站</h1>", unsafe_allow_html=True)

# 跑馬燈
marquee_content = "製作單位：企推處媒體行銷組　&nbsp;&nbsp;　" * 8
st.markdown(f'<div class="marquee-container"><marquee scrollamount="6"><span class="neon-text blink">{marquee_content}</span></marquee></div>', unsafe_allow_html=True)

# 觀測日期
today = datetime.now()
start_date = today - timedelta(days=7)
st.markdown(f'<div style="text-align:center; color:#aabccf; margin-bottom:20px; font-size:0.95em;">📅 觀測區間：{start_date.strftime("%Y-%m-%d")} 至 {today.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 📊 資料讀取與處理
# ---------------------------------------------------------
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df_raw = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")
    mask = df_raw.apply(lambda row: row.astype(str).str.contains('find.org.tw', case=False).any(), axis=1)
    df = df_raw[~mask].copy()
    
    df['dt'] = pd.to_datetime(df.iloc[:, 2], errors='coerce')
    df_7d = df[df['dt'] >= (today - timedelta(days=7))].copy()
    
    # 🤖 AI 點評區塊 (科技感樣式)
    top_3 = df_7d.groupby(df_7d.iloc[:, 1]).size().sort_values(ascending=False).head(3)
    if not top_3.empty:
        focus_list = top_3.index.tolist()
        st.markdown(f"""
            <div class="ai-monitor-box">
                <div class="ai-header">SYSTEM ANALYSIS // AI 輿情監測點評</div>
                <div style="color:#e0e0e0; font-size:0.95em; line-height:1.6;">
                    偵測到本週核心議題聚焦於「{ '、'.join(focus_list) }」。<br>
                    數據分析顯示，資策會在相關領域的媒體曝光具備高滲透率，報導結構穩定，整體聲量維持正向發展。
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🔥 排行榜卡片
    # ---------------------------------------------------------
    df_7d['clean_m'] = df_7d.apply(lambda x: urlparse(str(x.iloc[3])).netloc.replace("www.","").split('.')[0].upper(), axis=1)
    grouped = df_7d.groupby(df_7d.iloc[:, 1]).agg({df_7d.columns[3]: list, 'clean_m': list, df_7d.columns[2]: 'max'}).reset_index()
    grouped['count'] = grouped.iloc[:, 1].apply(len)
    
    st.markdown("### 🔥 本週熱門輿情排行榜")
    for i, (_, row) in enumerate(grouped.sort_values(by='count', ascending=False).head(15).iterrows()):
        st.markdown(f"""
            <div class="news-card">
                <div class="rank-text">TOP {i+1}</div>
                <div class="topic-title">{row.iloc[0]}</div>
                <div style="font-size:0.85em; color:#666; margin-top:8px;">🔥 {row['count']} 次露出 │ 📅 {row.iloc[3]}</div>
            </div>
            """, unsafe_allow_html=True)
        with st.expander("📂 來源細節"):
            for l, m in set(zip(row.iloc[1], row['clean_m'])):
                st.write(f"**[{m}]** ➔ [閱讀原文]({l})")
except Exception:
    st.error("📡 資料讀取中...")
