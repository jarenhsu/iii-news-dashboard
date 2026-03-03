import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, timedelta

# 1. 頁面風格：精簡版 AI 點評日誌與邊框整合
st.set_page_config(page_title="資策會新聞熱度觀測站", layout="centered")
st.markdown("""
    <style>
    /* 🌌 背景設定 */
    .stApp { 
        background: linear-gradient(135deg, #001226 0%, #001f3f 40%, #452000 100%);
        background-attachment: fixed;
        background-image: 
            linear-gradient(135deg, #001226 0%, #001f3f 40%, #452000 100%),
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), 
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 100% 100%, 35px 35px;
        color: #ffffff; 
        font-family: 'Consolas', 'Monaco', monospace; 
    }

    /* 🎬 標題區 */
    .header-container { text-align: center; padding: 45px 0; }
    .header-title { 
        position: relative; color: #ffffff !important; font-weight: 900; 
        letter-spacing: 12px; font-size: 2.8em; text-transform: uppercase;
        display: inline-block;
        filter: drop-shadow(0 0 10px #00d4ff);
    }
    .header-title::before, .header-title::after {
        content: "資策會新聞熱度觀測站";
        position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: transparent;
    }
    .header-title::before { color: #00d4ff; left: -3px; animation: glitch-anim-1 2s infinite linear alternate-reverse; }
    .header-title::after { color: #ff00ff; left: 3px; animation: glitch-anim-2 3s infinite linear alternate-reverse; }
    @keyframes glitch-anim-1 { 0% { clip: rect(20px, 9999px, 15px, 0); } 100% { clip: rect(60px, 9999px, 65px, 0); } }
    @keyframes glitch-anim-2 { 0% { clip: rect(50px, 9999px, 55px, 0); } 100% { clip: rect(90px, 9999px, 95px, 0); } }

    /* 💡 跑馬燈 */
    .marquee-container {
        background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(8px);
        border-top: 1px solid rgba(0, 212, 255, 0.3); border-bottom: 1px solid rgba(255, 165, 0, 0.3);
        padding: 10px 0; margin-bottom: 30px;
    }

    /* 🚀 整合式雷達邊框與精簡日誌內容 */
    .ai-monitor-wrapper {
        position: relative;
        width: 100%;
        margin-bottom: 40px;
        padding: 4px;
        background: rgba(10, 25, 47, 0.6);
        border-radius: 15px;
        overflow: hidden;
        z-index: 1;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .ai-monitor-wrapper::before {
        content: "";
        position: absolute; width: 200%; height: 200%;
        background: conic-gradient(#00d4ff, #FFA500, #ff00ff, #00d4ff);
        animation: rotate-border 6s linear infinite;
        z-index: -1;
    }
    @keyframes rotate-border { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

    .ai-monitor-box {
        position: relative;
        width: 100%;
        background: #001226;
        padding: 25px;
        border-radius: 12px;
        z-index: 2;
        box-shadow: inset 0 0 20px rgba(0, 212, 255, 0.2);
    }

    /* 日誌風緊湊排版 */
    .log-stream {
        font-size: 0.85em;
        line-height: 1.8;
        color: #00d4ff;
        text-align: justify;
    }
    .log-id { color: #FF8C00; font-weight: bold; margin-right: 4px; }
    .log-tag { color: #ffffff; background: rgba(255, 140, 0, 0.2); padding: 0 4px; border-radius: 2px; }

    /* 🏆 金色發光新聞卡片 */
    .news-card {
        background: rgba(255, 255, 255, 0.98); padding: 22px;
        border-radius: 15px; margin-bottom: 25px; color: #1a1a1a;
        border: 2px solid #FFD700; box-shadow: 0 0 15px rgba(255, 215, 0, 0.4);
    }
    .top-rank { color: #B8860B; font-weight: 900; font-size: 1.4em; display: block; }
    </style>
    """, unsafe_allow_html=True)

# 🎬 標題
st.markdown("<div class='header-container'><h1 class='header-title'>資策會新聞熱度觀測站</h1></div>", unsafe_allow_html=True)

# 跑馬燈
marquee_content = "DATA_SYNC: ACTIVE // 數據流即時更新中 // 企推處媒體行銷組 " * 5
st.markdown(f'<div class="marquee-container"><marquee scrollamount="6"><span style="color:#00d4ff; font-weight:bold;">{marquee_content}</span></marquee></div>', unsafe_allow_html=True)

# 📊 資料處理
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df_raw = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")
    mask = df_raw.apply(lambda row: row.astype(str).str.contains('find.org.tw', case=False).any(), axis=1)
    df = df_raw[~mask].copy()
    
    today = datetime.now()
    df['dt'] = pd.to_datetime(df.iloc[:, 2], errors='coerce')
    df_7d = df[df['dt'] >= (today - timedelta(days=7))].copy()
    
    grouped = df_7d.groupby(df_7d.iloc[:, 1]).agg({df_7d.columns[3]: list, df_7d.columns[2]: 'max'}).reset_index()
    grouped['count'] = grouped.iloc[:, 1].apply(len)
    ranked_df = grouped.sort_values(by='count', ascending=False).head(15)

    # 🤖 AI 監測：精簡數據日誌流排版
    if not ranked_df.empty:
        st.markdown('<div class="ai-monitor-wrapper"><div class="ai-monitor-box">', unsafe_allow_html=True)
        st.markdown('<div style="color:#FF8C00; font-weight:bold; margin-bottom:15px; font-size:0.9em;">[ ⚡ ANALYZING_HOT_DATA_LOGS ]</div>', unsafe_allow_html=True)
        
        # 建立一整塊日誌文字
        log_html = '<div class="log-stream">'
        for i, (_, row) in enumerate(ranked_df.iterrows()):
            tag = "HOT" if i == 0 else "STABLE" if i < 5 else "SCAN"
            short_title = row.iloc[0][:15] + "..." if len(row.iloc[0]) > 15 else row.iloc[0]
            log_html += f'<span class="log-id">[{i+1:02}]</span> <span class="log-tag">{tag}</span> {short_title} // '
        
        log_html += '<br><br><span style="color:#ffffff; opacity:0.8;">> 系統分析報告：本期輿情動能強勁，TOP 01 議題展現極高擴散率，其餘觀測項露出結構穩健，整體數據同步完成。</span>'
        log_html += '</div>'
        
        st.markdown(log_html, unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    # 🔥 排行榜清單
    st.markdown("<div style='color:#00d4ff; margin-bottom:15px; font-weight:bold;'>[ 📊 REAL_TIME_TRENDS ]</div>", unsafe_allow_html=True)
    for i, (_, row) in enumerate(ranked_df.iterrows()):
        st.markdown(f"""
            <div class="news-card">
                <span class="top-rank">TOP {i+1}</span>
                <div style="font-size:1.2em; font-weight:700; color:#001f3f; margin-bottom:8px;">{row.iloc[0]}</div>
                <div style="font-size:0.8em; color:#666; font-weight:bold;">🕒 TIMESTAMP: {row.iloc[2]}</div>
            </div>
            """, unsafe_allow_html=True)
except Exception:
    st.error("📡 DATA_SYNC_ERROR...")
