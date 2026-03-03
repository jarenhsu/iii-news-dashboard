import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# 1. 頁面風格：深藍至深橘漸層 + FB 粉專嵌入
st.set_page_config(page_title="資策會新聞熱度觀測站", layout="centered")

today = datetime.now()
seven_days_ago = today - timedelta(days=7)
date_display = f"{seven_days_ago.strftime('%Y.%m.%d')} - {today.strftime('%Y.%m.%d')}"

st.markdown(f"""
    <style>
    .stApp {{ 
        background: linear-gradient(135deg, #001226 0%, #001f3f 40%, #452000 100%);
        background-attachment: fixed;
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

    /* 📅 日期膠囊 */
    .date-pill {{
        text-align: center; margin: 0 auto 30px auto; font-size: 0.85em; color: #00d4ff;
        background: rgba(0, 212, 255, 0.1); border: 1px solid rgba(0, 212, 255, 0.3);
        padding: 5px 25px; border-radius: 50px; width: fit-content; letter-spacing: 2px;
    }}

    /* 🚀 AI 監測盒 */
    .ai-monitor-box {{ 
        background: rgba(10, 25, 47, 0.85); backdrop-filter: blur(12px); 
        padding: 25px; border-radius: 12px; border: 1px solid rgba(0, 212, 255, 0.2);
        margin-bottom: 40px;
    }}

    /* 🏆 新聞卡片 */
    .news-card {{
        background: rgba(255, 255, 255, 0.98); padding: 22px;
        border-radius: 15px; margin-bottom: 25px; color: #1a1a1a;
        border: 2px solid #FFD700; box-shadow: 0 0 15px rgba(255, 215, 0, 0.4);
    }}
    .top-rank {{ color: #B8860B; font-weight: 900; font-size: 1.5em; display: block; }}
    </style>
    """, unsafe_allow_html=True)

# 🎬 標題區
st.markdown("""<div class="header-container"><h1 class="header-title">資策會新聞熱度觀測站</h1></div>""", unsafe_allow_html=True)
st.markdown(f'<div class="date-pill">DATA RANGE: {date_display}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 📊 資料流處理
# ---------------------------------------------------------
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df_raw = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")
    mask = df_raw.apply(lambda row: row.astype(str).str.contains('find.org.tw', case=False).any(), axis=1)
    df = df_raw[~mask].copy()
    df['dt'] = pd.to_datetime(df.iloc[:, 2], errors='coerce')
    df_7d = df[df['dt'] >= seven_days_ago].copy()
    
    # AI 點評
    df_7d['clean_m'] = df_7d.apply(lambda x: urlparse(str(x.iloc[3])).netloc.replace("www.","").split('.')[0].upper(), axis=1)
    grouped = df_7d.groupby(df_7d.iloc[:, 1]).agg({df_7d.columns[3]: list, 'clean_m': list, df_7d.columns[2]: 'max'}).reset_index()
    grouped['count'] = grouped.iloc[:, 1].apply(len)
    ranked_df = grouped.sort_values(by='count', ascending=False)

    if not ranked_df.empty:
        top_1_title = ranked_df.iloc[0, 0]
        st.markdown(f"""
            <div class="ai-monitor-box">
                <div style="color:#00d4ff; font-size:0.85em; margin-bottom:10px;">> AI 深度數據分析啟動...</div>
                <div style="color:#ffffff; line-height:1.6;">
                    本週核心熱點新聞為：<strong>「{top_1_title}」</strong>。<br>
                    分析摘要：本期監測顯示該議題展現極高擴散動能，具備高度輿情價值。
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 📱 Facebook 粉專嵌入區塊
    st.markdown("<div style='color:#00d4ff; margin-bottom:15px; font-weight:bold; letter-spacing:1px;'>[ 📱 資策會 FB 官方情報 ]</div>", unsafe_allow_html=True)
    
    # 使用 Facebook Page Plugin
    fb_html = """
    <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 12px; text-align: center;">
        <iframe src="https://www.facebook.com/plugins/page.php?href=https%3A%2F%2Fwww.facebook.com%2Fmic.iii&tabs=timeline&width=500&height=500&small_header=false&adapt_container_width=true&hide_cover=false&show_facepile=true&appId" 
            width="100%" height="500" style="border:none;overflow:hidden" scrolling="no" frameborder="0" allowfullscreen="true" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe>
    </div>
    """
    components.html(fb_html, height=520)

    # ---------------------------------------------------------
    # 🔥 排行榜渲染
    # ---------------------------------------------------------
    st.markdown("<div style='color:#00d4ff; margin-top:30px; margin-bottom:15px; font-weight:bold; letter-spacing:1px;'>[ 📊 即時趨勢數據流 ]</div>", unsafe_allow_html=True)
    
    for i, (_, row) in enumerate(ranked_df.head(15).iterrows()):
        st.markdown(f"""
            <div class="news-card">
                <span class="top-rank">TOP {i+1}</span>
                <div class="topic-title">{row.iloc[0]}</div>
                <div style="font-size:0.85em; color:#555; font-weight:bold;">
                    📅 系統同步時間: {row.iloc[3]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with st.expander("查看原始來源數據"):
            for l, m in set(zip(row.iloc[1], row['clean_m'])):
                st.write(f"**[{m}]** ➔ [點擊閱讀原文]({l})")
except Exception as e:
    st.error("📡 資料同步中，請稍候...")
