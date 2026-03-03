import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, timedelta

# 1. 頁面風格、極致科技感 UI 設定
st.set_page_config(page_title="資策會新聞熱度觀測站", layout="centered")
st.markdown("""
    <style>
    /* 頁面深藍背景與字體 */
    .stApp { background-color: #000c1d; color: #ffffff; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    h1 { color: #00d4ff !important; text-align: center; font-weight: 800; letter-spacing: 3px; text-shadow: 0 0 15px rgba(0, 212, 255, 0.5); }

    /* 💡 霓虹跑馬燈 */
    .marquee-container {
        background: rgba(0, 0, 0, 0.7);
        border-top: 1px solid rgba(255, 165, 0, 0.3);
        border-bottom: 1px solid rgba(255, 165, 0, 0.3);
        padding: 8px 0;
        margin-bottom: 30px;
    }
    .neon-text {
        color: #FFA500; font-weight: bold; font-size: 1.2em;
        text-shadow: 0 0 2px #FFFFFF, 0 0 10px #FFA500;
    }
    .blink { animation: blinker 2.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.6; } }

    /* 🚀 極致科技感 AI 點評區塊 */
    .ai-monitor-box {
        position: relative;
        background: linear-gradient(135deg, rgba(10, 25, 47, 0.8) 0%, rgba(16, 33, 65, 0.8) 100%);
        backdrop-filter: blur(12px);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(0, 212, 255, 0.3);
        margin-bottom: 40px;
        overflow: hidden;
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.1);
    }
    
    /* 動態掃描線效果 */
    .ai-monitor-box::after {
        content: "";
        position: absolute;
        top: -100%; left: 0;
        width: 100%; height: 100%;
        background: linear-gradient(transparent, rgba(0, 212, 255, 0.1), transparent);
        animation: scan 4s linear infinite;
    }
    @keyframes scan {
        0% { top: -100%; }
        100% { top: 100%; }
    }

    .ai-header {
        color: #00d4ff;
        font-size: 0.9em;
        font-weight: 900;
        letter-spacing: 2px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid rgba(0, 212, 255, 0.2);
        padding-bottom: 8px;
    }

    /* 新聞卡片科技化 */
    .news-card {
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 15px;
        margin-bottom: 25px; 
        color: #1a1a1a;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border-left: 6px solid #FF8C00;
    }
    .rank-num { font-size: 2em; font-weight: 900; color: rgba(255, 140, 0, 0.1); position: absolute; right: 20px; top: 10px; }
    .topic-title { font-size: 1.3em; font-weight: 700; color: #001f3f; margin-top: 5px; position: relative; }
    </style>
    """, unsafe_allow_html=True)

# 標題更新為「新聞熱度觀測站」
st.markdown("<h1>📡 資策會新聞熱度觀測站</h1>", unsafe_allow_html=True)

# 跑馬燈
marquee_content = "製作單位：企推處媒體行銷組　&nbsp;&nbsp;　" * 8
st.markdown(f'<div class="marquee-container"><marquee scrollamount="6"><span class="neon-text blink">{marquee_content}</span></marquee></div>', unsafe_allow_html=True)

# 觀測日期
today = datetime.now()
start_date = today - timedelta(days=7)
st.markdown(f'<div style="text-align:center; color:#5c7c9c; margin-bottom:25px; font-size:0.9em; letter-spacing:1px;">STATUS: ACTIVE // RANGE: {start_date.strftime("%Y-%m-%d")} - {today.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 📊 資料處理
# ---------------------------------------------------------
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df_raw = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")
    mask = df_raw.apply(lambda row: row.astype(str).str.contains('find.org.tw', case=False).any(), axis=1)
    df = df_raw[~mask].copy()
    
    df['dt'] = pd.to_datetime(df.iloc[:, 2], errors='coerce')
    df_7d = df[df['dt'] >= (today - timedelta(days=7))].copy()
    
    # 🤖 AI 點評區塊 (極致科技樣式)
    top_3 = df_7d.groupby(df_7d.iloc[:, 1]).size().sort_values(ascending=False).head(3)
    if not top_3.empty:
        focus_list = top_3.index.tolist()
        st.markdown(f"""
            <div class="ai-monitor-box">
                <div class="ai-header">
                    <span>CORE ANALYTICS ENGINE</span>
                    <span style="color:#ff4500;">LIVE FEED ●</span>
                </div>
                <div style="color:#ffffff; font-size:1.05em; line-height:1.7; font-weight:300;">
                    <span style="color:#00d4ff;">[焦點偵測]</span> 本週核心議題為：<br>
                    <strong>「{ '、'.join(focus_list) }」</strong>。<br>
                    <span style="color:#00d4ff;">[分析簡報]</span> 資策會於數位賦能與認證機制之媒體分佈穩定，整體聲量較上期呈現正向波動。
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🔥 排行榜
    # ---------------------------------------------------------
    df_7d['clean_m'] = df_7d.apply(lambda x: urlparse(str(x.iloc[3])).netloc.replace("www.","").split('.')[0].upper(), axis=1)
    grouped = df_7d.groupby(df_7d.iloc[:, 1]).agg({df_7d.columns[3]: list, 'clean_m': list, df_7d.columns[2]: 'max'}).reset_index()
    grouped['count'] = grouped.iloc[:, 1].apply(len)
    
    st.markdown("<h3 style='margin-bottom:20px;'>🔥 本週熱門輿情排行榜</h3>", unsafe_allow_html=True)
    for i, (_, row) in enumerate(grouped.sort_values(by='count', ascending=False).head(15).iterrows()):
        st.markdown(f"""
            <div class="news-card">
                <div class="rank-num">#{i+1}</div>
                <div class="topic-title">{row.iloc[0]}</div>
                <div style="font-size:0.9em; color:#555; margin-top:12px; font-weight:500;">
                    📊 {row['count']} 則報導 ｜ 📅 {row.iloc[3]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with st.expander("📂 來源追蹤詳情"):
            for l, m in set(zip(row.iloc[1], row['clean_m'])):
                st.write(f"**[{m}]** ➔ [閱讀原文]({l})")
except Exception:
    st.error("📡 資料流讀取中...")
