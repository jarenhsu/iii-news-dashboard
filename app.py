import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, timedelta

# 1. 科技電影感視覺系統設定
st.set_page_config(page_title="資策會新聞熱度觀測站", layout="centered")
st.markdown("""
    <style>
    /* 🌌 深藍網格背景與數位字體 */
    .stApp { 
        background-color: #000c1d; 
        background-image: linear-gradient(rgba(0, 212, 255, 0.05) 1px, transparent 1px), 
                          linear-gradient(90deg, rgba(0, 212, 255, 0.05) 1px, transparent 1px);
        background-size: 30px 30px;
        color: #ffffff; 
        font-family: 'Consolas', 'Monaco', monospace; 
    }

    /* 🎬 科技電影感標題特效 */
    .header-container { text-align: center; padding: 40px 0; position: relative; }
    .header-title { 
        color: #00d4ff !important; 
        font-weight: 900; 
        letter-spacing: 10px; 
        font-size: 2.8em; 
        text-transform: uppercase;
        /* 霓虹發光效果 */
        text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff, 0 0 40px #00d4ff;
        animation: glitch 3s infinite;
    }
    
    /* 故障閃爍動畫 (Glitch Effect) */
    @keyframes glitch {
        0% { transform: skew(0deg); }
        2% { transform: skew(10deg); opacity: 0.8; }
        4% { transform: skew(-10deg); opacity: 0.9; }
        6% { transform: skew(0deg); }
        100% { transform: skew(0deg); }
    }

    .header-sub { 
        color: #00d4ff; 
        font-size: 0.8em; 
        letter-spacing: 5px; 
        opacity: 0.6;
        margin-top: 10px;
    }

    /* 💡 數據流跑馬燈 */
    .marquee-container {
        background: rgba(0, 0, 0, 0.8);
        border-top: 2px solid #00d4ff;
        border-bottom: 2px solid #00d4ff;
        padding: 10px 0;
        margin-bottom: 40px;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
    }
    .digital-text { color: #00d4ff; font-weight: bold; font-size: 1.1em; letter-spacing: 2px; }

    /* 🚀 旋轉邊框 AI 監測盒 */
    .ai-monitor-wrapper {
        position: relative; padding: 2px; background: transparent;
        border-radius: 10px; overflow: hidden; margin-bottom: 40px;
    }
    .ai-monitor-wrapper::before {
        content: ""; position: absolute; width: 150%; height: 150%;
        background: conic-gradient(#00d4ff, #ff4500, transparent 50%);
        animation: rotate-border 4s linear infinite; top: -25%; left: -25%;
    }
    @keyframes rotate-border { 100% { transform: rotate(360deg); } }
    .ai-monitor-box { position: relative; background: #001226; padding: 25px; border-radius: 8px; z-index: 1; }

    /* 🏆 金色發光新聞卡片 */
    .news-card {
        background: rgba(255, 255, 255, 0.98);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 30px;
        color: #1a1a1a;
        border: 2px solid #FFD700;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
        transition: all 0.3s ease-in-out;
    }
    .news-card:hover {
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.8);
    }
    .top-rank { color: #B8860B; font-weight: 900; font-size: 1.6em; margin-bottom: 10px; display: block; }
    .topic-title { font-size: 1.3em; font-weight: 700; color: #001f3f; line-height: 1.5; }
    </style>
    """, unsafe_allow_html=True)

# 🎬 標題區：加入 Glitch 特效
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">資策會新聞熱度觀測站</h1>
        <div class="header-sub">SYSTEM SECURE // DATA ENCRYPTED // ACTIVE</div>
    </div>
    """, unsafe_allow_html=True)

# 數據跑馬燈
marquee_content = "ANALYZING DATA FEED... [SUCCESS] // 企推處媒體行銷組 // LAST UPDATE: " + datetime.now().strftime("%H:%M:%S") + " &nbsp;&nbsp; " * 5
st.markdown(f'<div class="marquee-container"><marquee scrollamount="7"><span class="digital-text">{marquee_content}</span></marquee></div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 📊 資料流處理
# ---------------------------------------------------------
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df_raw = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")
    # 徹底過濾內部網頁
    mask = df_raw.apply(lambda row: row.astype(str).str.contains('find.org.tw', case=False).any(), axis=1)
    df = df_raw[~mask].copy()
    
    today = datetime.now()
    df['dt'] = pd.to_datetime(df.iloc[:, 2], errors='coerce')
    df_7d = df[df['dt'] >= (today - timedelta(days=7))].copy()
    
    # 🤖 AI 監測中心
    top_3 = df_7d.groupby(df_7d.iloc[:, 1]).size().sort_values(ascending=False).head(3)
    if not top_3.empty:
        st.markdown(f"""
            <div class="ai-monitor-wrapper">
                <div class="ai-monitor-box">
                    <div style="color:#00d4ff; font-size:0.8em; margin-bottom:10px;">> DEEP_DATA_SCAN_LOG_v4.0</div>
                    <div style="color:#00d4ff; line-height:1.8; font-size:1.1em;">
                        偵測到本週核心熱點：『{ ' / '.join(top_3.index.tolist()) }』。<br>
                        分析報告：本期聲量曲線穩定攀升，數位轉型相關話題在主流媒體之擴散效率極高。
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🔥 金色發光排行榜
    # ---------------------------------------------------------
    df_7d['clean_m'] = df_7d.apply(lambda x: urlparse(str(x.iloc[3])).netloc.replace("www.","").split('.')[0].upper(), axis=1)
    grouped = df_7d.groupby(df_7d.iloc[:, 1]).agg({df_7d.columns[3]: list, 'clean_m': list, df_7d.columns[2]: 'max'}).reset_index()
    grouped['count'] = grouped.iloc[:, 1].apply(len)
    
    st.markdown("<div style='color:#00d4ff; margin-bottom:20px; font-weight:bold; letter-spacing:2px;'>[ TOP_SALIENCE_REPORT ]</div>", unsafe_allow_html=True)
    
    for i, (_, row) in enumerate(grouped.sort_values(by='count', ascending=False).head(15).iterrows()):
        st.markdown(f"""
            <div class="news-card">
                <span class="top-rank">TOP {i+1}</span>
                <div class="topic-title">{row.iloc[0]}</div>
                <div style="font-size:0.9em; color:#444; margin-top:15px; font-weight:bold;">
                    📊 報導曝光量: {row['count']} ｜ 📅 系統觀測時間: {row.iloc[3]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with st.expander("DECRYPT_SOURCE_LINKS"):
            for l, m in set(zip(row.iloc[1], row['clean_m'])):
                st.write(f"**[{m}]** ➔ [VIEW_DATA]({l})")
except Exception:
    st.error("📡 SYSTEM_ALERT: UNABLE_TO_SYNC_DATA_STREAM")
