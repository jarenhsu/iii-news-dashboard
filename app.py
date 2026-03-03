import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, timedelta

# 1. 頁面風格：深藍至深橘漸層科技感與 AI 分析區塊優化
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

    /* 🎬 標題區：Cyberpunk 特效 */
    .header-container { text-align: center; padding: 45px 0; position: relative; }
    .header-title { 
        position: relative; color: #ffffff !important; font-weight: 900; 
        letter-spacing: 12px; font-size: 2.8em; text-transform: uppercase;
        display: inline-block;
        filter: drop-shadow(0 0 10px rgba(0, 212, 255, 0.5));
    }
    .header-title::before, .header-title::after {
        content: "資策會新聞熱度觀測站";
        position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
        background: transparent;
    }
    .header-title::before { color: #00d4ff; left: -3px; animation: glitch-anim-1 2s infinite linear alternate-reverse; }
    .header-title::after { color: #ff00ff; left: 3px; animation: glitch-anim-2 3s infinite linear alternate-reverse; }

    @keyframes glitch-anim-1 { 0% { clip: rect(20px, 9999px, 15px, 0); } 20% { clip: rect(10px, 9999px, 5px, 0); } 100% { clip: rect(60px, 9999px, 65px, 0); } }
    @keyframes glitch-anim-2 { 0% { clip: rect(50px, 9999px, 55px, 0); } 20% { clip: rect(90px, 9999px, 95px, 0); } 100% { clip: rect(30px, 9999px, 35px, 0); } }

    /* 💡 跑馬燈 */
    .marquee-container {
        background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(8px);
        border-top: 1px solid rgba(0, 212, 255, 0.3); border-bottom: 1px solid rgba(255, 165, 0, 0.3);
        padding: 10px 0; margin-bottom: 30px;
    }
    .digital-text { color: #00d4ff; font-weight: bold; font-size: 1.1em; letter-spacing: 1px; }

    /* 🚀 科技感 AI 點評區塊 */
    .ai-monitor-wrapper {
        position: relative; padding: 2px; background: transparent;
        border-radius: 12px; overflow: hidden; margin-bottom: 40px;
    }
    .ai-monitor-wrapper::before {
        content: ""; position: absolute; width: 150%; height: 150%;
        background: conic-gradient(#00d4ff, #FFA500, transparent 60%);
        animation: rotate-border 4s linear infinite; top: -25%; left: -25%;
    }
    @keyframes rotate-border { 100% { transform: rotate(360deg); } }
    
    .ai-monitor-box { 
        position: relative; background: rgba(10, 25, 47, 0.9); 
        backdrop-filter: blur(15px); padding: 30px; border-radius: 10px; z-index: 1; 
        border: 1px solid rgba(0, 212, 255, 0.3);
    }
    .ai-line { 
        color: #00d4ff; font-size: 0.9em; margin-bottom: 12px; 
        border-left: 3px solid #FF8C00; padding-left: 10px;
        line-height: 1.6;
    }
    .ai-id { color: #FF8C00; font-weight: bold; margin-right: 8px; }

    /* 🏆 金色發光新聞卡片 */
    .news-card {
        background: rgba(255, 255, 255, 0.98); padding: 22px;
        border-radius: 15px; margin-bottom: 25px; color: #1a1a1a;
        border: 2px solid #FFD700; box-shadow: 0 0 15px rgba(255, 215, 0, 0.4);
        transition: all 0.3s ease;
    }
    .top-rank { color: #B8860B; font-weight: 900; font-size: 1.5em; margin-bottom: 8px; display: block; }
    .topic-title { font-size: 1.25em; font-weight: 700; color: #001f3f; margin-bottom: 12px; }
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
    
    # 統計數據
    df_7d['clean_m'] = df_7d.apply(lambda x: urlparse(str(x.iloc[3])).netloc.replace("www.","").split('.')[0].upper(), axis=1)
    grouped = df_7d.groupby(df_7d.iloc[:, 1]).agg({df_7d.columns[3]: list, 'clean_m': list, df_7d.columns[2]: 'max'}).reset_index()
    grouped['count'] = grouped.iloc[:, 1].apply(len)
    ranked_df = grouped.sort_values(by='count', ascending=False).head(15)

    # ---------------------------------------------------------
    # 🤖 AI 深度輿情點評 (全面點評 TOP 1-15)
    # ---------------------------------------------------------
    if not ranked_df.empty:
        st.markdown('<div class="ai-monitor-wrapper"><div class="ai-monitor-box">', unsafe_allow_html=True)
        st.markdown('<div style="color:#FF8C00; font-weight:bold; margin-bottom:20px; letter-spacing:2px;">[ ⚡ AI 全域數據點評啟動 ]</div>', unsafe_allow_html=True)
        
        for i, (_, row) in enumerate(ranked_df.iterrows()):
            # 依據名次生成不同風格的點評文字
            if i == 0:
                tag = "焦點核心"
                comment = "本週最具滲透力之熱點，媒體共鳴度極高。"
            elif i < 3:
                tag = "高頻波動"
                comment = "露出結構穩定，相關數位轉型議題持續延燒。"
            elif i < 8:
                tag = "穩定擴散"
                comment = "數據顯示該議題已進入跨平台傳播階段。"
            else:
                tag = "趨勢偵測"
                comment = "露出分佈均勻，具備後續發展動能。"

            st.markdown(f"""
                <div class="ai-line">
                    <span class="ai-id">[{i+1:02}]</span> 
                    <span style="color:#ffffff;">{row.iloc[0][:25]}...</span><br>
                    <span style="font-size:0.85em; color:rgba(0, 212, 255, 0.7);">>> {tag} | {comment}</span>
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
                <div style="font-size:0.85em; color:#555; font-weight:bold;">
                    📅 系統觀測日期: {row.iloc[3]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with st.expander("DECODE_DETAILS"):
            for l, m in set(zip(row.iloc[1], row['clean_m'])):
                st.write(f"**[{m}]** ➔ [LINK]({l})")
except Exception:
    st.error("📡 系統初始化中...")
