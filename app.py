import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, timedelta

# 1. 儀表板視覺系統設定
st.set_page_config(page_title="資策會新聞熱度觀測站", layout="centered")
st.markdown("""
    <style>
    /* 🌌 深藍網格背景設定 */
    .stApp { 
        background-color: #000c1d; 
        background-image: linear-gradient(rgba(0, 212, 255, 0.05) 1px, transparent 1px), 
                          linear-gradient(90deg, rgba(0, 212, 255, 0.05) 1px, transparent 1px);
        background-size: 30px 30px; /* 網格大小 */
        color: #ffffff; 
        font-family: 'Consolas', 'Monaco', monospace; 
    }

    /* 標題與裝飾 */
    .header-container { text-align: center; padding: 20px 0; position: relative; }
    .header-title { color: #00d4ff !important; font-weight: 800; letter-spacing: 5px; margin: 0; font-size: 2.2em; }
    .header-sub { color: #5c7c9c; font-size: 0.7em; letter-spacing: 2px; }

    /* 💡 數位數據流跑馬燈 */
    .marquee-container {
        background: rgba(0, 12, 29, 0.9);
        border-top: 1px solid #00d4ff;
        border-bottom: 1px solid #00d4ff;
        padding: 8px 0;
        margin-bottom: 30px;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.1);
    }
    .digital-text { color: #00d4ff; font-weight: bold; font-size: 1.1em; letter-spacing: 1px; }

    /* 🚀 旋轉邊框 AI 監測盒 (核心儀表板組件) */
    .ai-monitor-wrapper {
        position: relative;
        padding: 2px;
        background: transparent;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 40px;
    }
    .ai-monitor-wrapper::before {
        content: "";
        position: absolute;
        width: 150%; height: 150%;
        background: conic-gradient(#00d4ff, #ff4500, transparent 50%);
        animation: rotate-border 5s linear infinite;
        top: -25%; left: -25%;
    }
    @keyframes rotate-border { 100% { transform: rotate(360deg); } }

    .ai-monitor-box {
        position: relative;
        background: #001226;
        padding: 20px;
        border-radius: 8px;
        z-index: 1;
        border: 1px solid rgba(0, 212, 255, 0.2);
    }
    .ai-tag { background: #ff4500; color: white; padding: 2px 8px; font-size: 0.7em; border-radius: 3px; margin-right: 10px; }

    /* 📋 新聞數據卡片 */
    .news-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
        color: #1a1a1a;
        border-left: 5px solid #00d4ff;
        box-shadow: 6px 6px 0px rgba(0, 212, 255, 0.2);
    }
    .rank-id { color: #00d4ff; font-weight: bold; font-size: 0.9em; margin-bottom: 5px; display: block; }
    .topic-title { font-size: 1.2em; font-weight: 700; color: #001f3f; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 儀表板標題區
st.markdown("""
    <div class="header-container">
        <div class="header-sub">INTELLIGENCE MONITORING SYSTEM v3.0</div>
        <h1 class="header-title">資策會新聞熱度觀測站</h1>
    </div>
    """, unsafe_allow_html=True)

# 數據跑馬燈
marquee_content = "LOADING DATA... [OK] // 企推處媒體行銷組 // STATUS: ONLINE &nbsp;&nbsp; " * 6
st.markdown(f'<div class="marquee-container"><marquee scrollamount="6"><span class="digital-text">{marquee_content}</span></marquee></div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 📊 資料流處理
# ---------------------------------------------------------
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df_raw = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")
    # 徹底移除 find.org.tw
    mask = df_raw.apply(lambda row: row.astype(str).str.contains('find.org.tw', case=False).any(), axis=1)
    df = df_raw[~mask].copy()
    
    today = datetime.now()
    df['dt'] = pd.to_datetime(df.iloc[:, 2], errors='coerce')
    df_7d = df[df['dt'] >= (today - timedelta(days=7))].copy()
    
    # 🤖 AI 監測報告區
    top_3 = df_7d.groupby(df_7d.iloc[:, 1]).size().sort_values(ascending=False).head(3)
    if not top_3.empty:
        st.markdown(f"""
            <div class="ai-monitor-wrapper">
                <div class="ai-monitor-box">
                    <div style="margin-bottom:10px;"><span class="ai-tag">AI ANALYSIS</span><span style="color:#5c7c9c; font-size:0.8em;">REPORT_ID: {today.strftime('%y%m%d')}</span></div>
                    <div style="color:#00d4ff; line-height:1.6;">
                        > 偵測到本週高熱度議題：『{ ' / '.join(top_3.index.tolist()) }』。<br>
                        > 系統評估：資策會相關動態之曝光分佈符合預期，整體聲量處於擴張階段。
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🔥 數據排名列表
    # ---------------------------------------------------------
    df_7d['clean_m'] = df_7d.apply(lambda x: urlparse(str(x.iloc[3])).netloc.replace("www.","").split('.')[0].upper(), axis=1)
    grouped = df_7d.groupby(df_7d.iloc[:, 1]).agg({df_7d.columns[3]: list, 'clean_m': list, df_7d.columns[2]: 'max'}).reset_index()
    grouped['count'] = grouped.iloc[:, 1].apply(len)
    
    st.markdown("<div style='color:#00d4ff; margin-bottom:15px; font-weight:bold;'>[ TOP_RANKING_FEED ]</div>", unsafe_allow_html=True)
    for i, (_, row) in enumerate(grouped.sort_values(by='count', ascending=False).head(15).iterrows()):
        st.markdown(f"""
            <div class="news-card">
                <span class="rank-id">LOG_ENTRY_{i+1:02}</span>
                <div class="topic-title">{row.iloc[0]}</div>
                <div style="font-size:0.85em; color:#555;">
                    OCCURRENCE: {row['count']} ｜ SYNC_TIME: {row.iloc[3]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with st.expander("DECODE_SOURCE_DATA"):
            for l, m in set(zip(row.iloc[1], row['clean_m'])):
                st.write(f"**[{m}]** ➔ [GO_TO_LINK]({l})")
except Exception:
    st.error("📡 CONNECTION_ERROR: DATA_FEED_INTERRUPTED")
