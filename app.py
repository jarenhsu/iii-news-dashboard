import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, timedelta

# 1. 頁面風格、閃爍發光與無縫跑馬燈設定
st.set_page_config(page_title="資策會輿情熱度觀測站", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #001f3f; color: #ffffff; }
    h1 { color: #ffffff !important; text-align: center; }

    /* 💡 無縫循環跑馬燈與霓虹發光效果 */
    .marquee-wrapper {
        overflow: hidden;
        white-space: nowrap;
        background: rgba(0, 0, 0, 0.3);
        padding: 10px 0;
        margin-bottom: 25px;
        border-top: 1px solid #FF4500;
        border-bottom: 1px solid #FF4500;
    }

    .marquee-content {
        display: inline-block;
        padding-left: 100%;
        animation: marquee 15s linear infinite;
        color: #FF4500;
        font-weight: bold;
        font-size: 1.5em; /* 文字小一號 */
        text-shadow: 0 0 10px #FF4500, 0 0 20px #FF8C00; /* 霓虹發亮效果 */
    }

    /* 閃爍動畫 */
    .blink { animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.5; } }

    /* 無縫移動動畫 */
    @keyframes marquee {
        0% { transform: translate(0, 0); }
        100% { transform: translate(-100%, 0); }
    }

    /* 新聞卡片效果 */
    .news-card {
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 15px;
        margin-bottom: 30px; 
        color: #333333;
        box-shadow: 0 0 15px #FF8C00;
        transition: transform 0.3s;
    }
    .rank-text { color: #FF8C00; font-weight: 900; font-size: 1.6em; }
    .topic-title { font-size: 1.35em; font-weight: 700; color: #001f3f; margin-top: 10px; }
    .ai-box { background-color: #1a3a5a; padding: 20px; border-radius: 12px; border: 1px solid #FF8C00; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 資策會輿情熱度觀測站</h1>", unsafe_allow_html=True)

# ✨ 無縫重複、閃爍發光的跑馬燈
# 透過重複文字內容來確保視覺上的不間斷感
marquee_text = "企推處媒體行銷組　　　　　" * 5 
st.markdown(f"""
    <div class="marquee-wrapper">
        <div class="marquee-content blink">
            製作單位：{marquee_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

# 💡 觀測日期與資料邏輯
today = datetime.now()
start_date = today - timedelta(days=7)
st.markdown(f'<div style="text-align:center; color:#aabccf; margin-bottom:20px;">📅 觀測區間：{start_date.strftime("%Y-%m-%d")} 至 {today.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 📊 資料讀取 (排除 find.org.tw 與識別媒體)
# ---------------------------------------------------------
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def get_clean_media(raw_m, url):
    mapping = {"yahoo": "Yahoo新聞", "udn": "聯合新聞網", "ltn": "自由時報", "chinatimes": "中時新聞網", "cna": "中央社", "rti.org.tw": "央廣 RTI"}
    domain = urlparse(str(url)).netloc.lower()
    for key, name in mapping.items():
        if key in domain: return name
    return domain.replace("www.", "").split('.')[0].upper()

try:
    df_raw = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")
    # 全局排除 find.org.tw
    df = df_raw[~df_raw.apply(lambda r: r.astype(str).str.contains('find.org.tw', case=False).any(), axis=1)].copy()
    
    df['dt'] = pd.to_datetime(df.iloc[:, 2], errors='coerce')
    df_7d = df[df['dt'] >= (today - timedelta(days=7))].copy()
    
    # AI 點評
    top_3 = df_7d.groupby(df_7d.iloc[:, 1]).size().sort_values(ascending=False).head(3)
    if not top_3.empty:
        st.markdown('<div class="ai-box">✨ <strong>AI 輿情監測點評</strong>', unsafe_allow_html=True)
        st.write(f"本週核心話題集中於「{ '、'.join(top_3.index.tolist()) }」。資策會在數位領域的聲量穩健發展。")
        st.markdown('</div>', unsafe_allow_html=True)

    # 排行榜
    df_7d['clean_m'] = df_7d.apply(lambda x: get_clean_media(x.iloc[5], x.iloc[3]), axis=1)
    grouped = df_7d.groupby(df_7d.iloc[:, 1]).agg({df_7d.columns[3]: list, 'clean_m': list, df_7d.columns[2]: 'max'}).reset_index()
    grouped['count'] = grouped.iloc[:, 1].apply(len)
    
    st.markdown("### 🔥 本週熱門輿情排行榜")
    for i, (_, row) in enumerate(grouped.sort_values(by='count', ascending=False).head(15).iterrows()):
        st.markdown(f"""
            <div class="news-card">
                <div class="rank-text">TOP {i+1}</div>
                <div class="topic-title">{row.iloc[0]}</div>
                <div style="font-size:0.9em; color:#666; margin-top:10px;">🔥 {row['count']} 次露出 │ 📅 {row.iloc[3]}</div>
            </div>
            """, unsafe_allow_html=True)
        with st.expander("📂 來源細節"):
            for l, m in set(zip(row.iloc[1], row['clean_m'])):
                st.write(f"**[{m}]** ➔ [閱讀原文]({l})")
except Exception:
    st.error("📡 資料更新中...")
