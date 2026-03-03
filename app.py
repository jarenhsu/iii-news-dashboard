import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, timedelta

# 1. 科技電影感視覺系統設定 (移除模糊發光，改用銳利錯位)
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

    /* 🎬 帥氣銳利：Cyberpunk 雙色錯位標題 */
    .header-container { text-align: center; padding: 45px 0; position: relative; }
    
    .header-title { 
        position: relative;
        color: #ffffff !important; /* 主文字為純白，確保清晰 */
        font-weight: 900; 
        letter-spacing: 12px; 
        font-size: 2.8em; 
        text-transform: uppercase;
        display: inline-block;
        /* 💡 防止發光導致模糊 */
        text-shadow: None !important; 
    }

    /* 💡 錯位特效層 (青藍與洋紅) */
    .header-title::before,
    .header-title::after {
        content: "資策會新聞熱度觀測站";
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: #000c1d; /* 遮罩底色 */
    }

    /* 青藍錯位層 */
    .header-title::before {
        color: #00d4ff;
        left: -3px; /* 向左錯位 */
        text-shadow: 1px 0 #00d4ff;
        animation: glitch-anim-1 2s infinite linear alternate-reverse;
    }

    /* 洋紅錯位層 */
    .header-title::after {
        color: #ff00ff;
        left: 3px; /* 向右錯位 */
        text-shadow: -1px 0 #ff00ff;
        animation: glitch-anim-2 3s infinite linear alternate-reverse;
    }

    /* 錯位動畫 */
    @keyframes glitch-anim-1 {
        0% { clip: rect(20px, 9999px, 15px, 0); }
        10% { clip: rect(80px, 9999px, 85px, 0); }
        20% { clip: rect(10px, 9999px, 5px, 0); }
        100% { clip: rect(60px, 9999px, 65px, 0); }
    }
    @keyframes glitch-anim-2 {
        0% { clip: rect(50px, 9999px, 55px, 0); }
        10% { clip: rect(10px, 9999px, 15px, 0); }
        20% { clip: rect(90px, 9999px, 95px, 0); }
        100% { clip: rect(30px, 9999px, 35px, 0); }
    }

    .header-sub { 
        color: #00d4ff; font-size: 0.8em; letter-spacing: 5px; opacity: 0.7; margin-top: 15px;
    }

    /* 數據流跑馬燈 */
    .marquee-container {
        background: rgba(0, 0, 0, 0.8);
        border-top: 2px solid #00d4ff;
        border-bottom: 2px solid #00d4ff;
        padding: 10px 0;
        margin-bottom: 40px;
    }
    .digital-text { color: #00d4ff; font-weight: bold; font-size: 1.1em; letter-spacing: 2px; }

    /* 🏆 金色發光新聞卡片 */
    .news-card {
        background: rgba(255, 255, 255, 0.98);
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 30px;
        color: #1a1a1a;
        border: 2px solid #FFD700;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
        transition: transform 0.3s ease-in-out;
    }
    .news-card:hover { transform: scale(1.02); box-shadow: 0 0 30px rgba(255, 215, 0, 0.8); }
    .top-rank { color: #B8860B; font-weight: 900; font-size: 1.6em; margin-bottom: 10px; display: block; }
    .topic-title { font-size: 1.3em; font-weight: 700; color: #001f3f; line-height: 1.5; }
    </style>
    """, unsafe_allow_html=True)

# 🎬 帥氣錯位標題區
st.markdown("""
    <div class="header-container">
        <h1 class="header-title" data-text="資策會新聞熱度觀測站">資策會新聞熱度觀測站</h1>
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
    mask = df_raw.apply(lambda row: row.astype(str).str.contains('find.org.tw', case=False).any(), axis=1)
    df = df_raw[~mask].copy()
    
    today = datetime.now()
    df['dt'] = pd.to_datetime(df.iloc[:, 2], errors='coerce')
    df_7d = df[df['dt'] >= (today - timedelta(days=7))].copy()
    
    # 🤖 AI 監測中心
    top_3 = df_7d.groupby(df_7d.iloc[:, 1]).size().sort_values(ascending=False).head(3)
    if not top_3.empty:
        st.markdown(f"""
            <div style="background:#1a3a5a; padding:20px; border-radius:10px; border:1px solid #00d4ff; margin-bottom:40px; color:#00d4ff;">
                > DEEP_DATA_SCAN_LOG_v4.1<br>
                > 偵測到本週核心熱點：『{ ' / '.join(top_3.index.tolist()) }』。<br>
                > 分析報告：資策會相關動態在數位人才話題之聲量分佈健全，媒體曝光結構穩定。
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
