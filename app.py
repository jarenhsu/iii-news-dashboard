import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, timedelta

# 1. 頁面風格：深藍至深橘漸層科技感 UI 設定
st.set_page_config(page_title="資策會月度新聞熱度觀測", layout="centered")

# --- 修改處：將觀測天數調整為 30 天 ---
today = datetime.now()
observation_days = 30 
start_date = today - timedelta(days=observation_days)
date_display = f"{start_date.strftime('%Y.%m.%d')} - {today.strftime('%Y.%m.%d')}"

st.markdown(f"""
    <style>
    /* 🌌 背景設定 */
    .stApp {{ 
        background: linear-gradient(135deg, #001226 0%, #001f3f 40%, #452000 100%);
        background-attachment: fixed;
        background-image: 
            linear-gradient(135deg, #001226 0%, #001f3f 40%, #452000 100%),
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), 
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 100% 100%, 35px 35px;
        color: #ffffff; 
        font-family: 'Consolas', 'Monaco', monospace; 
    }}

    /* 🎬 標題區 */
    .header-container {{ text-align: center; padding: 45px 0 10px 0; position: relative; }}
    .header-title {{ 
        position: relative; color: #ffffff !important; font-weight: 900; 
        letter-spacing: 12px; font-size: 2.8em; text-transform: uppercase;
        display: inline-block; filter: drop-shadow(0 0 10px rgba(0, 212, 255, 0.5));
    }}

    /* 📅 月度觀測日期膠囊 */
    .date-pill {{
        text-align: center; margin: 0 auto 30px auto; font-size: 0.85em; color: #FFA500;
        background: rgba(255, 165, 0, 0.1); border: 1px solid rgba(255, 165, 0, 0.3);
        padding: 5px 25px; border-radius: 50px; width: fit-content; letter-spacing: 2px;
        box-shadow: 0 0 15px rgba(255, 165, 0, 0.2);
    }}

    /* 🚀 AI 監測盒 */
    .ai-monitor-wrapper {{
        position: relative; padding: 2px; background: transparent;
        border-radius: 12px; overflow: hidden; margin-bottom: 40px;
    }}
    .ai-monitor-wrapper::before {{
        content: ""; position: absolute; width: 150%; height: 150%;
        background: conic-gradient(#FFA500, #00d4ff, transparent 60%);
        animation: rotate-border 4s linear infinite; top: -25%; left: -25%;
    }}
    @keyframes rotate-border {{ 100% {{ transform: rotate(360deg); }} }}
    .ai-monitor-box {{ 
        position: relative; background: rgba(10, 25, 47, 0.9); 
        backdrop-filter: blur(12px); padding: 25px; border-radius: 10px; z-index: 1; 
        border: 1px solid rgba(255, 165, 0, 0.2);
    }}

    /* 🏆 前五名金色新聞卡片 */
    .news-card {{
        background: rgba(255, 255, 255, 0.98); padding: 22px;
        border-radius: 15px; margin-bottom: 25px; color: #1a1a1a;
        border: 2px solid #FFD700; box-shadow: 0 0 15px rgba(255, 215, 0, 0.4);
        transition: all 0.3s ease;
    }}
    .news-card:hover {{ transform: translateY(-5px); box-shadow: 0 0 30px rgba(255, 215, 0, 0.7); }}
    .top-rank {{ color: #B8860B; font-weight: 900; font-size: 1.5em; margin-bottom: 8px; display: block; }}
    .topic-title {{ font-size: 1.25em; font-weight: 700; color: #001f3f; margin-bottom: 12px; }}
    </style>
    """, unsafe_allow_html=True)

# 🎬 標題區
st.markdown("""<div class="header-container"><h1 class="header-title">資策會新聞熱度觀測站</h1></div>""", unsafe_allow_html=True)
st.markdown(f'<div class="date-pill">30-DAY MONTHLY REPORT: {date_display}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 📊 資料流處理
# ---------------------------------------------------------
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df_raw = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")
    mask = df_raw.apply(lambda row: row.astype(str).str.contains('find.org.tw', case=False).any(), axis=1)
    df = df_raw[~mask].copy()
    
    # 篩選最近 30 天
    df['dt'] = pd.to_datetime(df.iloc[:, 2], errors='coerce')
    df_filtered = df[df['dt'] >= start_date].copy()
    
    # 數據統計
    df_filtered['clean_m'] = df_filtered.apply(lambda x: urlparse(str(x.iloc[3])).netloc.replace("www.","").split('.')[0].upper(), axis=1)
    grouped = df_filtered.groupby(df_filtered.iloc[:, 1]).agg({df_filtered.columns[3]: list, 'clean_m': list, df_filtered.columns[2]: 'max'}).reset_index()
    grouped['count'] = grouped.iloc[:, 1].apply(len)
    ranked_df = grouped.sort_values(by='count', ascending=False)

    if not ranked_df.empty:
        # AI 點評
        top_1_title = ranked_df.iloc[0, 0]
        st.markdown(f"""
            <div class="ai-monitor-wrapper">
                <div class="ai-monitor-box">
                    <div style="color:#FFA500; font-size:0.85em; margin-bottom:10px;">> 月度大數據深度分析中...</div>
                    <div style="color:#ffffff; line-height:1.6;">
                        本月<strong>輿情影響力之冠</strong>為：<strong>「{top_1_title}」</strong>。<br>
                        分析摘要：在過去 30 天的觀測期內，該議題展現了極具韌性的媒體生命週期，報導量持續領先，代表其社會討論價值極高。
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🔥 前五名精選排行榜
    # ---------------------------------------------------------
    st.markdown("<div style='color:#FFD700; margin-bottom:15px; font-weight:bold; letter-spacing:1px;'>[ 🏆 月度熱度前五強 ]</div>", unsafe_allow_html=True)
    
    top_5_df = ranked_df.head(5)
    others_df = ranked_df.iloc[5:20] # 月報可以看稍微多一點潛力熱點

    for i, (_, row) in enumerate(top_5_df.iterrows()):
        st.markdown(f"""
            <div class="news-card">
                <span class="top-rank">TOP {i+1}</span>
                <div class="topic-title">{row.iloc[0]}</div>
                <div style="font-size:0.85em; color:#555; font-weight:bold;">
                    📅 最後更新日期: {row.iloc[3]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with st.expander(f"查看數據來源"):
            for l, m in set(zip(row.iloc[1], row['clean_m'])):
                st.write(f"**[{m}]** ➔ [點擊閱讀原文]({l})")

    # ---------------------------------------------------------
    # 📦 月度延伸觀察 (TOP 6-20)
    # ---------------------------------------------------------
    if not others_df.empty:
        st.markdown("<div style='color:#00d4ff; margin-top:30px; margin-bottom:10px; font-weight:bold;'>[ 📡 月度潛力趨勢回顧 ]</div>", unsafe_allow_html=True)
        with st.expander("展開其餘熱門報導 (TOP 6 - TOP 20)"):
            for i, (_, row) in enumerate(others_df.iterrows()):
                st.markdown(f"""
                    <div style="padding:10px; border-bottom:1px solid rgba(255,255,255,0.1);">
                        <span style="color:#00d4ff; font-weight:bold;">#{i+6}</span> 
                        <span style="margin-left:10px;">{row.iloc[0]}</span>
                    </div>
                    """, unsafe_allow_html=True)

except Exception:
    st.error("📡 月度數據計算中，請稍候...")
