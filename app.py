import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, timedelta

# 1. 頁面風格：徹底解決邊框與文字分離問題
st.set_page_config(page_title="資策會新聞熱度觀測站", layout="centered")
st.markdown("""
    <style>
    /* 🌌 背景設定 */
    .stApp { 
        background: linear-gradient(135deg, #001226 0%, #001f3f 40%, #452000 100%);
        background-attachment: fixed;
        color: #ffffff; 
        font-family: 'Consolas', 'Monaco', monospace; 
    }

    /* 🎬 標題區：Cyberpunk 雙色錯位 */
    .header-container { text-align: center; padding: 45px 0; }
    .header-title { 
        position: relative; color: #ffffff !important; font-weight: 900; 
        letter-spacing: 12px; font-size: 2.8em; text-transform: uppercase;
        display: inline-block;
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

    /* 🚀 核心修正：確保文字絕對在框內 */
    .ai-monitor-wrapper {
        position: relative;
        width: 100%;
        min-height: 250px; /* 預設最小高度 */
        margin-bottom: 40px;
        border-radius: 15px;
        overflow: hidden; /* 切割外溢光芒 */
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 4px; /* 旋轉邊框顯露的寬度 */
    }

    /* 旋轉霓虹背景層 */
    .ai-monitor-wrapper::before {
        content: "";
        position: absolute;
        width: 250%; height: 250%;
        background: conic-gradient(#00d4ff, #FFA500, #ff00ff, #00d4ff);
        animation: rotate-border 6s linear infinite;
        z-index: 0;
    }
    @keyframes rotate-border { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

    /* 內部內容盒：完全覆蓋中心並鎖定文字 */
    .ai-monitor-box {
        position: relative;
        width: 100%;
        height: 100%;
        background: #001226; /* 完全不透明背景，擋住光芒中心 */
        padding: 25px;
        border-radius: 12px;
        z-index: 10; /* 確保在光芒上方 */
        box-shadow: inset 0 0 20px rgba(0, 212, 255, 0.2);
    }

    .log-stream { font-size: 0.85em; line-height: 1.8; color: #00d4ff; text-align: justify; }
    .log-id { color: #FF8C00; font-weight: bold; margin-right: 4px; }
    .log-tag { color: #ffffff; background: rgba(255, 140, 0, 0.3); padding: 0 4px; border-radius: 2px; }

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

    # 🤖 修正版 AI 監測：文字必須在框內
    if not ranked_df.empty:
        # 💡 重點：將文字 HTML 完整包裹在 ai-monitor-box 內部
        ai_html = '<div class="ai-monitor-wrapper"><div class="ai-monitor-box">'
        ai_html += '<div style="color:#FF8C00; font-weight:bold; margin-bottom:15px; font-size:0.9em;">[ ⚡ ANALYZING_HOT_DATA_LOGS ]</div>'
        ai_html += '<div class="log-stream">'
        
        for i, (_, row) in enumerate(ranked_df.iterrows()):
            tag = "HOT" if i == 0 else "STABLE" if i < 5 else "SCAN"
            short_title = row.iloc[0][:15] + "..." if len(row.iloc[0]) > 15 else row.iloc[0]
            ai_html += f'<span class="log-id">[{i+1:02}]</span> <span class="log-tag">{tag}</span> {short_title} // '
        
        ai_html += '<br><br><span style="color:#ffffff; opacity:0.8;">> 系統分析報告：本期輿情動能強勁，數據同步完成。</span>'
        ai_html += '</div></div></div>'
        
        st.markdown(ai_html, unsafe_allow_html=True)

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
