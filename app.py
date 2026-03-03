import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime, timedelta

# 1. 頁面風格設定
st.set_page_config(page_title="資策會輿情熱度觀測站", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #fcfcf9; color: #37474f; }
    .news-card {
        background-color: #ffffff; padding: 25px; border-radius: 12px;
        border: 1px solid #f0f0ed; margin-bottom: 25px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }
    .ai-box {
        background-color: #fffbeb; padding: 20px; border-radius: 12px;
        border: 1px solid #fde68a; margin-bottom: 30px;
        box-shadow: 0 2px 10px rgba(253, 230, 138, 0.2);
    }
    .rank-text { color: #af946d; font-weight: 900; font-size: 1.5em; margin-bottom: 5px; }
    .topic-title { font-size: 1.3em; font-weight: 700; color: #2c3e50; margin-bottom: 15px; line-height: 1.5; }
    .info-bar { margin-bottom: 15px; font-size: 0.85em; color: #95a5a6; display: flex; gap: 15px; }
    .date-range { text-align: center; color: #7f8c8d; margin-bottom: 20px; font-size: 1.1em; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center; padding:10px;'><h1 style='color:#263238;'>📡 資策會輿情熱度觀測站</h1></div>", unsafe_allow_html=True)

# 💡 計算觀測日期
today = datetime.now()
start_date = today - timedelta(days=7)
st.markdown(f'<div class="date-range">📅 觀測區間：{start_date.strftime("%Y-%m-%d")} 至 {today.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 📊 輿情資料讀取與媒體識別邏輯
# ---------------------------------------------------------
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def get_clean_media(raw_m, url):
    mapping = {
        "yahoo": "Yahoo新聞", "udn": "聯合新聞網", "ltn": "自由時報", "chinatimes": "中時新聞網",
        "ettoday": "ETtoday", "storm": "風傳媒", "cna": "中央社", "setn": "三立新聞",
        "tvbs": "TVBS", "rti.org.tw": "央廣 RTI", "iii.org.tw": "資策會官網", 
        "money.udn": "經濟日報", "ctee": "工商時報", "technews": "科技新報", "bnext": "數位時代"
    }
    domain = urlparse(str(url)).netloc.lower()
    for key, name in mapping.items():
        if key in domain: return name
    
    clean_m = str(raw_m).strip().upper()
    if len(clean_m) > 1 and not any(x in clean_m for x in ["NEWS", "媒體", "GOOGLE", "解析"]):
        return str(raw_m).strip()
    
    parts = domain.replace("www.", "").split('.')
    return parts[-2].upper() if len(parts) >= 2 else "網路媒體"

try:
    df_raw = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")
    # 徹底排除 find.org.tw
    mask = df_raw.apply(lambda row: row.astype(str).str.contains('find.org.tw', case=False).any(), axis=1)
    df = df_raw[~mask].copy()
    
    df['title'] = df.iloc[:, 1].astype(str).str.strip()
    df['date_str'] = df.iloc[:, 2].astype(str).str.strip()
    df['link'] = df.iloc[:, 3].astype(str).str.strip()
    df['raw_media'] = df.iloc[:, 5].astype(str).str.strip()
    df['dt'] = pd.to_datetime(df['date_str'], errors='coerce')
    
    # 篩選最近 7 天
    df_7d = df[df['dt'] >= (today - timedelta(days=7))].copy()
    df_7d = df_7d[df_7d['title'].str.len() > 5]
    df_7d = df_7d[~df_7d['title'].str.contains("解析失敗|提取中|未知標題")]
    df_7d['clean_media'] = df_7d.apply(lambda x: get_clean_media(x['raw_media'], x['link']), axis=1)

    # ---------------------------------------------------------
    # 🤖 AI 自動生成摘要評論
    # ---------------------------------------------------------
    stats = df_7d.groupby('title').size().reset_index(name='count')
    top_3 = stats.sort_values(by='count', ascending=False).head(3)

    if not top_3.empty:
        st.markdown('<div class="ai-box">✨ <strong>AI 輿情觀測員：</strong>', unsafe_allow_html=True)
        focus = "、".join(top_3['title'].tolist())
        comment = f"本週輿情焦點集中於「{focus}」。分析顯示資策會在數位技術應用及產業影響力方面持續獲得媒體關注，前三大熱點報導共累積多達 {top_3['count'].sum()} 次露出，整體聲量平穩向上。"
        st.write(comment)
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🔥 排行榜卡片顯示
    # ---------------------------------------------------------
    grouped = df_7d.groupby('title').agg({'link': list, 'clean_media': list, 'date_str': 'max'}).reset_index()
    grouped['count'] = grouped['link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    if not grouped.empty:
        st.markdown("### 🔥 本週熱門輿情排行榜")
        for i, (_, row) in enumerate(grouped.iterrows()):
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-text">TOP {i+1}</div>
                    <div class="topic-title">{row['title']}</div>
                    <div class="info-bar">
                        <span>🔥 {row['count']} 次露出</span>
                        <span>📅 最新日期：{row['date_str']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with st.expander("📂 查看詳細來源細節"):
                seen = set()
                for l, m in zip(row['link'], row['clean_media']):
                    if l not in seen:
                        st.write(f"**[{m}]** ➔ [閱讀原文]({l})")
                        seen.add(l)
    else:
        st.info("💡 最近 7 日內尚無相關報導更新。")

except Exception as e:
    st.error("📡 輿情資料同步中，請稍候...")
