import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, timedelta

# 1. 頁面風格：修正 AI 框框溢出問題與視覺優化
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
        filter: drop-shadow(0 0 10px rgba(0, 212, 255, 0.5));
    }
    .header-title::before, .header-title::after {
        content: "資策會新聞熱度觀測站";
        position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: transparent;
    }
    .header-title::before { color: #00d4ff; left: -3px; animation: glitch-anim-1 2s infinite linear alternate-reverse; }
    .header-title::after { color: #ff00ff; left: 3px; animation: glitch-anim-2 3s infinite linear alternate-reverse; }
    @keyframes glitch-anim-1 { 0% { clip: rect(20px, 9999px, 15px, 0); } 100% { clip: rect(60px, 9999px, 65px, 0); } }
    @keyframes glitch-anim-2 { 0% { clip: rect(50px, 9999px, 55px, 0); } 100% { clip: rect(30px, 9999px, 35px, 0); } }

    /* 💡 跑馬燈 */
    .marquee-container {
        background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(8px);
        border-top: 1px solid rgba(0, 212, 255, 0.3); border-bottom: 1px solid rgba(255, 165, 0, 0.3);
        padding: 10px 0; margin-bottom: 30px;
    }
    .digital-text { color: #00d4ff; font-weight: bold; font-size: 1.1em; }

    /* 🚀 AI 監測盒：修正定位與自動高度 */
    .ai-monitor-wrapper {
        position: relative; 
        padding: 2px; 
        background: transparent;
        border-radius: 12px; 
        overflow: hidden; /* 確保旋轉邊框不外溢 */
        margin-bottom: 40px;
        width: 100%;
    }
    .ai-monitor-wrapper::before {
        content: ""; position: absolute; width: 150%; height: 150%;
        background: conic-gradient(#00d4ff, #FFA500, transparent 60%);
        animation: rotate-border 4s linear infinite; top: -25%; left: -25%;
    }
    @keyframes rotate-border { 100% { transform: rotate(360deg); } }
    
    .ai-monitor-box { 
        position: relative; 
        background: rgba(10, 25, 47, 0.95); /* 增加不透明度 */
        backdrop-filter: blur(15px); 
        padding: 25px; 
        border-radius: 10px; 
        z-index: 1; 
        border: 1px solid rgba(0, 212, 255, 0.2);
        max-height: 600px; /* 防止過長 */
        overflow-y: auto;  /* 若內容真的超長則內部捲動 */
    }
    .ai-line { 
        color: #00d4ff; font-size: 0.85em; margin-bottom: 10px; 
        border-left: 3px solid #FF8C00; padding-left: 10px;
        line-height: 1.5;
    }
    .ai-id { color: #FF8C00; font-weight: bold; margin-right: 5px; }

    /* 🏆 金色發光卡片 */
    .news-card {
        background: rgba(255, 255, 255, 0.98); padding: 22px;
        border-radius: 15px; margin-bottom: 25px; color: #1a1a1a;
        border: 2px solid #FFD700; box-shadow: 0 0 15px rgba(255, 215, 0, 0.4);
    }
    .top-rank { color: #B8860B; font-weight: 900; font-size: 1.5em; margin-bottom: 8px; display: block; }
    .topic-title { font-size: 1.25em; font-weight: 700; color: #001f3f; }
    </style>
    """, unsafe_allow_html=True)

# 🎬 標題
st.markdown("<div class='header-container'><h1 class='header-title'>資策會新聞熱度觀測站</h1></div>", unsafe_allow_html=True)

# 跑馬燈
marquee_content = "SYSTEM_SYNC: ACTIVE // 企推處媒體行銷組 // 數據封包傳輸中... " * 5
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
    
    df_7d['clean_m'] = df_7d.apply(lambda x: urlparse(str(x.iloc[3])).netloc.replace("www.","").split('.')[0].upper(), axis=1)
    grouped = df_7d.groupby(df_7d.iloc[:, 1]).agg({df_7d.columns[3]: list, 'clean_m': list, df_7d.columns[2]: 'max'}).reset_index()
    grouped['count'] = grouped.iloc[:, 1].apply(len)
    ranked_df = grouped.sort_values(by='count', ascending=False).head(15)

    # ---------------------------------------------------------
    # 🤖 AI 深度輿情點評 (修正定位版)
    # ---------------------------------------------------------
    if not ranked_df.empty:
        st.markdown('<div class="ai-monitor-wrapper"><div class="ai-monitor-box">', unsafe_allow_html=True)
        st.markdown('<div style="color:#FF8C00; font-weight:bold; margin-bottom:15px; letter-spacing:1px; font-size:0.9em;">[ ⚡ AI 全域數據監測中 ]</div>', unsafe_allow_html=True)
        
        for i, (_, row) in enumerate(ranked_df.iterrows()):
            tag = "焦點" if i == 0 else "穩定" if i < 5 else "偵測"
            comment = "本週焦點熱點" if i == 0 else "報導結構穩定" if i < 5 else "具備後續動能"
            
            # 💡 限制標題長度避免擠出框框
            short_title = row.iloc[0][:28] + "..." if len(row.iloc[0]) > 28 else row.iloc[0]
            
            st.markdown(f"""
                <div class="ai-line">
                    <span class="ai-id">[{i+1:02}]</span> 
                    <span style="color:#ffffff;">{short_title}</span><br>
                    <span style="font-size:0.8em; color:rgba(0, 212, 255, 0.6);">>> {tag} | {comment}</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🔥 排行榜卡片
    # ---------------------------------------------------------
    st.markdown("<div style='color:#00d4ff; margin-bottom:15px; font-weight:bold; letter-spacing:1px;'>[ 📊 即時趨勢數據清單 ]</div>", unsafe_allow_html=True)
    
    for i, (_, row) in enumerate(ranked_df.iterrows()):
        st.markdown(f"""
            <div class="news-card">
                <span class="top-rank">TOP {i+1}</span>
                <div class="topic-title">{row.iloc[0]}</div>
                <div style="font-size:0.85em; color:#555; font-weight:bold; margin-top:8px;">
                    📅 系統觀測日期: {row.iloc[3]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with st.expander("DECODE_DETAILS"):
            for l, m in set(zip(row.iloc[1], row['clean_m'])):
                st.write(f"**[{m}]** ➔ [LINK]({l})")
except Exception:
    st.error("📡 系統初始化中...")
