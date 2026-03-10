import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, timedelta

# 1. 頁面風格設定
st.set_page_config(page_title="資策會月度新聞熱度觀測", layout="centered")

# 設定觀測天數為 30 天
today = datetime.now()
start_date = today - timedelta(days=30)
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
    .header-container {{ text-align: center; padding: 45px 0 10px 0; }}
    .header-title {{ 
        color: #ffffff !important; font-weight: 900; 
        letter-spacing: 12px; font-size: 2.8em; text-transform: uppercase;
        filter: drop-shadow(0 0 10px rgba(0, 212, 255, 0.5));
    }}

    /* 📅 月度觀測日期膠囊 */
    .date-pill {{
        text-align: center; margin: 0 auto 30px auto; font-size: 0.85em; color: #FFA500;
        background: rgba(255, 165, 0, 0.1); border: 1px solid rgba(255, 165, 0, 0.3);
        padding: 5px 25px; border-radius: 50px; width: fit-content; letter-spacing: 2px;
    }}

    /* 🚀 AI 監測盒 */
    .ai-monitor-wrapper {{
        position: relative; padding: 2px; border-radius: 12px; overflow: hidden; margin-bottom: 40px;
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

    /* 🏆 TOP 1-5 金色卡片 */
    .news-card-gold {{
        background: rgba(255, 255, 255, 0.98); padding: 20px;
        border-radius: 15px; margin-bottom: 20px; color: #1a1a1a;
        border: 2px solid #FFD700; box-shadow: 0 0 15px rgba(255, 215, 0, 0.3);
    }}
    .top-rank-gold {{ color: #B8860B; font-weight: 900; font-size: 1.4em; }}

    /* 🥈 TOP 6-10 藍色卡片 */
    .news-card-blue {{
        background: rgba(10, 25, 47, 0.6); padding: 15px;
        border-radius: 12px; margin-bottom: 15px; color: #ffffff;
        border: 1px solid rgba(0, 212, 255, 0.4); backdrop-filter: blur(5px);
    }}
    .top-rank-blue {{ color: #00d4ff; font-weight: 800; font-size: 1.1em; }}
    </style>
    """, unsafe_allow_html=True)

# 🎬 標題區
st.markdown("""<div class="header-container"><h1 class="header-title">資策會新聞熱度觀測站</h1></div>""", unsafe_allow_html=True)
st.markdown(f'<div class="date-pill">30-DAY MONTHLY ANALYTICS: {date_display}</div>', unsafe_allow_html=True)

# 📊 資料流處理
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df_raw = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")
    mask = df_raw.apply(lambda row: row.astype(str).str.contains('find.org.tw', case=False).any(), axis=1)
    df = df_raw[~mask].copy()
    
    df['dt'] = pd.to_datetime(df.iloc[:, 2], errors='coerce')
    df_filtered = df[df['dt'] >= start_date].copy()
    
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
                    <div style="color:#FFA500; font-size:0.85em; margin-bottom:10px;">> 月度深度分析報告摘要...</div>
                    <div style="color:#ffffff; line-height:1.6;">
                        本月<strong>影響力焦點</strong>：<strong>「{top_1_title}」</strong>。<br>
                        分析摘要：本話題在 30 日觀測期內橫跨多個媒體平台，其露出廣度與持久度展現了顯著的社群討論價值。
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🔥 排行榜呈現 (TOP 1-10)
    # ---------------------------------------------------------
    st.markdown("<div style='color:#FFD700; margin-bottom:15px; font-weight:bold; letter-spacing:1px;'>[ 🏆 月度輿情熱度前十強 ]</div>", unsafe_allow_html=True)
    
    top_10_df = ranked_df.head(10)

    for i, (_, row) in enumerate(top_10_df.iterrows()):
        rank = i + 1
        if rank <= 5:
            # 前五名使用金色大卡片
            st.markdown(f"""
                <div class="news-card-gold">
                    <span class="top-rank-gold">TOP {rank}</span>
                    <div style="font-size:1.2em; font-weight:700; color:#001f3f; margin:8px 0;">{row.iloc[0]}</div>
                    <div style="font-size:0.8em; color:#666;">📅 最後更新: {row.iloc[3]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # 六到十名使用精簡藍色卡片
            st.markdown(f"""
                <div class="news-card-blue">
                    <span class="top-rank-blue">TOP {rank}</span>
                    <span style="margin-left:15px; font-weight:600;">{row.iloc[0]}</span>
                    <div style="font-size:0.75em; color:#aaa; margin-top:5px; margin-left:65px;">📅 {row.iloc[3]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with st.expander(f"查看來源數據"):
            for l, m in set(zip(row.iloc[1], row['clean_m'])):
                st.write(f"**[{m}]** ➔ [閱讀原文]({l})")

except Exception:
    st.error("📡 數據同步中...")
