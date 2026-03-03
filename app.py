import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, timedelta

# 1. 頁面風格：深灰玻璃科技感 UI 設定
st.set_page_config(page_title="資策會新聞熱度觀測站", layout="centered")
st.markdown("""
    <style>
    /* 🌌 深灰玻璃背景與數位網格 */
    .stApp { 
        background-color: #121212; 
        background-image: 
            radial-gradient(circle at 50% 50%, rgba(40, 40, 40, 0.5), #121212),
            linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px), 
            linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px);
        background-size: 100% 100%, 40px 40px;
        color: #e0e0e0; 
        font-family: 'Consolas', 'Monaco', monospace; 
    }

    /* 🎬 標題區：Cyberpunk 雙色錯位 */
    .header-container { text-align: center; padding: 45px 0; position: relative; }
    .header-title { 
        position: relative; color: #ffffff !important; font-weight: 900; 
        letter-spacing: 12px; font-size: 2.8em; text-transform: uppercase;
        display: inline-block; text-shadow: None !important; 
    }
    .header-title::before, .header-title::after {
        content: "資策會新聞熱度觀測站";
        position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #121212;
    }
    .header-title::before {
        color: #00d4ff; left: -3px; text-shadow: 1px 0 #00d4ff;
        animation: glitch-anim-1 2s infinite linear alternate-reverse;
    }
    .header-title::after {
        color: #ff00ff; left: 3px; text-shadow: -1px 0 #ff00ff;
        animation: glitch-anim-2 3s infinite linear alternate-reverse;
    }
    @keyframes glitch-anim-1 {
        0% { clip: rect(20px, 9999px, 15px, 0); }
        20% { clip: rect(10px, 9999px, 5px, 0); }
        100% { clip: rect(60px, 9999px, 65px, 0); }
    }
    @keyframes glitch-anim-2 {
        0% { clip: rect(50px, 9999px, 55px, 0); }
        20% { clip: rect(90px, 9999px, 95px, 0); }
        100% { clip: rect(30px, 9999px, 35px, 0); }
    }

    /* 💡 數據流跑馬燈 */
    .marquee-container {
        background: rgba(20, 20, 20, 0.8);
        backdrop-filter: blur(5px);
        border-top: 1px solid rgba(0, 212, 255, 0.3);
        border-bottom: 1px solid rgba(0, 212, 255, 0.3);
        padding: 8px 0;
        margin-bottom: 30px;
    }
    .digital-text { color: #00d4ff; font-weight: bold; font-size: 1.1em; letter-spacing: 1px; }

    /* 🚀 核心雷達旋轉邊框 AI 監測盒 */
    .ai-monitor-wrapper {
        position: relative; padding: 2px; background: transparent;
        border-radius: 12px; overflow: hidden; margin-bottom: 40px;
    }
    .ai-monitor-wrapper::before {
        content: ""; position: absolute; width: 150%; height: 150%;
        background: conic-gradient(#00d4ff, #ff4500, transparent 50%);
        animation: rotate-border 5s linear infinite; top: -25%; left: -25%;
    }
    @keyframes rotate-border { 100% { transform: rotate(360deg); } }
    .ai-monitor-box { 
        position: relative; background: rgba(30, 30, 30, 0.9); 
        backdrop-filter: blur(10px); padding: 25px; border-radius: 10px; z-index: 1; 
    }

    /* 🏆 金色發光玻璃卡片 */
    .news-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 22px;
        border-radius: 12px;
        margin-bottom: 25px;
        color: #1a1a1a;
        border: 2px solid #FFD700;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.4);
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .news-card:hover { 
        transform: translateY(-5px); 
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.7); 
        background: rgba(255, 255, 255, 1);
    }
    .top-rank { color: #B8860B; font-weight: 900; font-size: 1.4em; margin-bottom: 8px; display: block; }
    .topic-title { font-size: 1.25em; font-weight: 700; color: #001f3f; margin-bottom: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 🎬 標題區
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">資策會新聞熱度觀測站</h1>
        <div style="color:#5c7c9c; font-size:0.7em; letter-spacing:2px; margin-top:10px;">TACTICAL INTELLIGENCE DISPLAY // CORE v4.6</div>
    </div>
    """, unsafe_allow_html=True)

# 跑馬燈
marquee_content = "SYSTEM_READY... [OK] // 企推處媒體行銷組 // LAST_SYNC: " + datetime.now().strftime("%H:%M") + " &nbsp;&nbsp; " * 6
st.markdown(f'<div class="marquee-container"><marquee scrollamount="6"><span class="digital-text">{marquee_content}</span></marquee></div>', unsafe_allow_html=True)

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
    
    # 🤖 AI 監測區塊 (雷達旋轉邊框)
    top_3 = df_7d.groupby(df_7d.iloc[:, 1]).size().sort_values(ascending=False).head(3)
    if not top_3.empty:
        st.markdown(f"""
            <div class="ai-monitor-wrapper">
                <div class="ai-monitor-box">
                    <div style="color:#00d4ff; font-size:0.85em; margin-bottom:10px;">> SCANNING_WEEKLY_TRENDS... [DONE]</div>
                    <div style="color:#00d4ff; line-height:1.6;">
                        偵測到本週熱門關鍵字：『{ ' / '.join(top_3.index.tolist()) }』。<br>
                        系統分析：媒體報導結構穩定，數位化相關話題在特定頻道的傳播效能優異。
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
    
    st.markdown("<div style='color:#00d4ff; margin-bottom:15px; font-weight:bold; letter-spacing:1px;'>[ LIVE_DATA_STREAM ]</div>", unsafe_allow_html=True)
    
    for i, (_, row) in enumerate(grouped.sort_values(by='count', ascending=False).head(15).iterrows()):
        st.markdown(f"""
            <div class="news-card">
                <span class="top-rank">TOP {i+1}</span>
                <div class="topic-title">{row.iloc[0]}</div>
                <div style="font-size:0.85em; color:#555;">
                    📊 露出頻次: {row['count']} ｜ 📅 更新時間: {row.iloc[3]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with st.expander("DECODE_DETAILS"):
            for l, m in set(zip(row.iloc[1], row['clean_m'])):
                st.write(f"**[{m}]** ➔ [LINK]({l})")
except Exception:
    st.error("📡 DATA_SYNC_ERROR")
