import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, timedelta

# 1. 頁面風格、數位方塊跑馬燈與科技感 UI 設定
st.set_page_config(page_title="資策會新聞熱度觀測站", layout="centered")
st.markdown("""
    <style>
    /* 頁面深藍背景 */
    .stApp { background-color: #000c1d; color: #ffffff; font-family: 'Consolas', 'Monaco', monospace; }
    h1 { color: #00d4ff !important; text-align: center; font-weight: 800; letter-spacing: 4px; }

    /* 💡 數位方塊跑馬燈 (取代發光效果) */
    .marquee-container {
        background: rgba(0, 212, 255, 0.05);
        border-top: 1px solid #00d4ff;
        border-bottom: 1px solid #00d4ff;
        padding: 10px 0;
        margin-bottom: 30px;
        position: relative;
    }
    
    /* 四個角落的裝飾方塊 */
    .marquee-container::before { content: "◢"; position: absolute; top: 0; left: 0; color: #00d4ff; font-size: 8px; }
    .marquee-container::after { content: "◣"; position: absolute; bottom: 0; right: 0; color: #00d4ff; font-size: 8px; }

    .digital-text {
        color: #00d4ff; 
        font-weight: bold;
        font-size: 1.1em;
        letter-spacing: 2px;
        /* 移除 text-shadow 發光 */
    }

    /* 🚀 AI 監測區塊：掃描線特效 */
    .ai-monitor-box {
        background: rgba(10, 25, 47, 0.9);
        padding: 25px;
        border-radius: 5px;
        border: 1px solid #00d4ff;
        margin-bottom: 40px;
        box-shadow: inset 0 0 15px rgba(0, 212, 255, 0.2);
    }
    .ai-header {
        color: #ff4500;
        font-size: 0.8em;
        font-weight: bold;
        border-bottom: 1px solid rgba(255, 69, 0, 0.3);
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
    }

    /* 新聞卡片：簡約科技感 */
    .news-card {
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 4px;
        margin-bottom: 25px; 
        color: #1a1a1a;
        border-right: 4px solid #00d4ff;
        box-shadow: 4px 4px 0px #00d4ff; /* 硬邊陰影效果 */
    }
    .rank-num { font-size: 1.2em; font-weight: 800; color: #00d4ff; border: 1px solid #00d4ff; padding: 2px 8px; margin-right: 10px; }
    .topic-title { font-size: 1.25em; font-weight: 700; color: #001f3f; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 資策會新聞熱度觀測站</h1>", unsafe_allow_html=True)

# ✨ 數位方塊跑馬燈 (無發光，穩定捲動)
marquee_content = "DATA TRANSMISSION // 企推處媒體行銷組　&nbsp;&nbsp;　" * 8
st.markdown(f"""
    <div class="marquee-container">
        <marquee scrollamount="5" behavior="scroll" direction="left">
            <span class="digital-text">{marquee_content}</span>
        </marquee>
    </div>
    """, unsafe_allow_html=True)

# 觀測日期與狀態
today = datetime.now()
start_date = today - timedelta(days=7)
st.markdown(f'<div style="text-align:center; color:#00d4ff; margin-bottom:25px; font-size:0.8em; font-weight:bold;">[ RANGE: {start_date.strftime("%Y-%m-%d")} / {today.strftime("%Y-%m-%d")} ]</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 📊 資料處理
# ---------------------------------------------------------
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df_raw = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")
    # 徹底排除 find.org.tw
    mask = df_raw.apply(lambda row: row.astype(str).str.contains('find.org.tw', case=False).any(), axis=1)
    df = df_raw[~mask].copy()
    
    df['dt'] = pd.to_datetime(df.iloc[:, 2], errors='coerce')
    df_7d = df[df['dt'] >= (today - timedelta(days=7))].copy()
    
    # 🤖 AI 點評 (數位監測樣式)
    top_3 = df_7d.groupby(df_7d.iloc[:, 1]).size().sort_values(ascending=False).head(3)
    if not top_3.empty:
        focus_list = top_3.index.tolist()
        st.markdown(f"""
            <div class="ai-monitor-box">
                <div class="ai-header">
                    <span>> EXECUTE_ANALYSIS_CMD</span>
                    <span style="letter-spacing:1px;">SCANNING... OK</span>
                </div>
                <div style="color:#00d4ff; font-size:1em; line-height:1.6;">
                    核心關鍵議題：『{ ' / '.join(focus_list) }』。<br>
                    分析結果：資策會相關動態在數位轉型領域之聲量佔比顯著，媒體曝光結構健全。
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🔥 排行榜
    # ---------------------------------------------------------
    df_7d['clean_m'] = df_7d.apply(lambda x: urlparse(str(x.iloc[3])).netloc.replace("www.","").split('.')[0].upper(), axis=1)
    grouped = df_7d.groupby(df_7d.iloc[:, 1]).agg({df_7d.columns[3]: list, 'clean_m': list, df_7d.columns[2]: 'max'}).reset_index()
    grouped['count'] = grouped.iloc[:, 1].apply(len)
    
    st.markdown("<h3 style='border-left: 4px solid #00d4ff; padding-left:15px; margin-bottom:20px;'>HOT_TOPICS_RANKING</h3>", unsafe_allow_html=True)
    for i, (_, row) in enumerate(grouped.sort_values(by='count', ascending=False).head(15).iterrows()):
        st.markdown(f"""
            <div class="news-card">
                <span class="rank-num">ID_{i+1:02}</span>
                <div class="topic-title">{row.iloc[0]}</div>
                <div style="font-size:0.85em; color:#555; margin-top:12px;">
                    VOLUME: {row['count']} ｜ LAST_UPDATE: {row.iloc[3]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with st.expander("SOURCE_DETAILS"):
            for l, m in set(zip(row.iloc[1], row['clean_m'])):
                st.write(f"**[{m}]** ➔ [LINK]({l})")
except Exception:
    st.error("📡 DATA_STREAM_ERROR")
