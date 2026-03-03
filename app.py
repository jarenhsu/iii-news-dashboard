import streamlit as st
import pandas as pd
from urllib.parse import urlparse
import altair as alt

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
    .rank-text { color: #af946d; font-weight: 900; font-size: 1.5em; margin-bottom: 5px; }
    .topic-title { font-size: 1.3em; font-weight: 700; color: #2c3e50; margin-bottom: 15px; line-height: 1.5; }
    .info-bar { margin-bottom: 15px; font-size: 0.85em; color: #95a5a6; display: flex; gap: 15px; }
    .chart-container { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #f0f0ed; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center; padding:20px;'><h1 style='color:#263238;'>📡 資策會輿情熱度觀測站</h1></div>", unsafe_allow_html=True)

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# 💡 媒體名稱辨識與補位系統
def get_clean_media(raw_m, url):
    mapping = {
        "yahoo": "Yahoo新聞", "udn": "聯合新聞網", "ltn": "自由時報", "chinatimes": "中時新聞網",
        "ettoday": "ETtoday", "storm": "風傳媒", "cna": "中央社", "setn": "三立新聞",
        "tvbs": "TVBS", "ebc": "東森新聞", "ftv": "民視新聞", "mnews": "鏡新聞",
        "money.udn": "經濟日報", "ctee": "工商時報", "technews": "科技新報", "bnext": "數位時代",
        "rti.org.tw": "央廣 RTI", "find.org.tw": "FIND中心", "iii.org.tw": "資策會官網"
    }
    domain = urlparse(str(url)).netloc.lower()
    for key, name in mapping.items():
        if key in domain: return name
    clean_m = str(raw_m).strip()
    if len(clean_m) > 1 and not any(x in clean_m.upper() for x in ["媒體", "NEWS", "GOOGLE", "解析"]):
        return clean_m
    parts = domain.replace("www.", "").split('.')
    return parts[0].upper() if parts else "網路媒體"

try:
    # 2. 讀取並清洗資料
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")
    df['title'] = df.iloc[:, 1].astype(str).str.strip()
    df['date'] = df.iloc[:, 2].astype(str).str.strip()
    df['link'] = df.iloc[:, 3].astype(str).str.strip()
    df['raw_media'] = df.iloc[:, 5].astype(str).str.strip() # F 欄媒體

    # 排除解析失敗的無效資料
    df = df[df['title'].str.len() > 5]
    df = df[~df['title'].str.contains("解析失敗|提取中|未知標題")]
    
    # 為每一列應用媒體辨識
    df['clean_media'] = df.apply(lambda x: get_clean_media(x['raw_media'], x['link']), axis=1)

    # 📊 3. 新增：媒體分佈圖表區塊
    st.markdown("### 📊 媒體曝光分佈")
    media_counts = df['clean_media'].value_counts().reset_index()
    media_counts.columns = ['媒體名稱', '報導次數']
    top_media = media_counts.head(10) # 顯示前 10 名

    chart = alt.Chart(top_media).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
        x=alt.X('報導次數:Q', title='露出次數'),
        y=alt.Y('媒體名稱:N', sort='-x', title=None),
        color=alt.Color('報導次數:Q', scale=alt.Scale(scheme='goldorange'), legend=None),
        tooltip=['媒體名稱', '報導次數']
    ).properties(height=350)

    st.altair_chart(chart, use_container_width=True)
    st.markdown("---")

    # 4. 數據聚合與新聞卡片
    grouped = df.groupby('title').agg({'link': list, 'clean_media': list, 'date': 'max'}).reset_index()
    grouped['count'] = grouped['link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    if grouped.empty:
        st.info("💡 目前尚無有效新聞標題。")
    else:
        st.markdown(f"### 🔥 熱門輿情排行榜 (共 {len(df)} 則報導)")
        for i, (_, row) in enumerate(grouped.iterrows()):
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-text">TOP {i+1}</div>
                    <div class="topic-title">{row['title']}</div>
                    <div class="info-bar">
                        <span>🔥 {row['count']} 次報導</span>
                        <span>📅 最新日期：{row['date']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with st.expander(f"📂 查看詳細來源"):
                seen_links = set()
                for l, m in zip(row['link'], row['clean_media']):
                    if l not in seen_links:
                        st.write(f"**[{m}]** ➔ [閱讀原文]({l})")
                        seen_links.add(l)

except Exception as e:
    st.error(f"系統資料同步中...")
