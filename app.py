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
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center; padding:20px;'><h1 style='color:#263238;'>📡 資策會輿情熱度觀測站</h1></div>", unsafe_allow_html=True)

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# 💡 媒體辨識系統
def get_clean_media(raw_m, url):
    mapping = {
        "yahoo": "Yahoo新聞", "udn": "聯合新聞網", "ltn": "自由時報", "chinatimes": "中時新聞網",
        "ettoday": "ETtoday", "storm": "風傳媒", "cna": "中央社", "setn": "三立新聞",
        "tvbs": "TVBS", "rti.org.tw": "央廣 RTI", "find.org.tw": "FIND中心", "iii.org.tw": "資策會官網"
    }
    domain = urlparse(str(url)).netloc.lower()
    for key, name in mapping.items():
        if key in domain: return name
    return "網路媒體"

try:
    # 2. 讀取資料
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")

    # 💡 關鍵：在任何處理之前，徹底移除 find.org.tw 的所有行
    # 我們針對「新聞連結」這一直欄（索引為 3）進行過濾
    df = df[~df.iloc[:, 3].astype(str).str.contains("find.org.tw", na=False)]

    # 3. 欄位對位
    df['title'] = df.iloc[:, 1].astype(str).str.strip()
    df['date'] = df.iloc[:, 2].astype(str).str.strip()
    df['link'] = df.iloc[:, 3].astype(str).str.strip()
    df['raw_media'] = df.iloc[:, 5].astype(str).str.strip()

    # 4. 數據過濾
    df = df[df['title'].str.len() > 5]
    df = df[~df['title'].str.contains("解析失敗|提取中|未知標題")]
    df['clean_media'] = df.apply(lambda x: get_clean_media(x['raw_media'], x['link']), axis=1)

    # 📊 5. 媒體分佈圖 (此時 find.org.tw 已不計入)
    st.markdown("### 📊 外部媒體曝光分佈")
    media_counts = df['clean_media'].value_counts().reset_index()
    media_counts.columns = ['媒體名稱', '報導次數']
    st.altair_chart(alt.Chart(media_counts.head(10)).mark_bar().encode(
        x='報導次數:Q', y=alt.Y('媒體名稱:N', sort='-x'), color='報導次數:Q'
    ).properties(height=300), use_container_width=True)

    st.markdown("---")

    # 6. 重新分組統計熱度
    # 因為 find.org.tw 已經被移除，所以原本的 TOP 1 就會自動消失
    grouped = df.groupby('title').agg({'link': list, 'clean_media': list, 'date': 'max'}).reset_index()
    grouped['count'] = grouped['link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    if grouped.empty:
        st.info("💡 資料同步中...")
    else:
        st.markdown("### 🔥 熱門輿情排行榜 (已徹底排除 find.org.tw)")
        for i, (_, row) in enumerate(grouped.iterrows()):
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-text">TOP {i+1}</div>
                    <div class="topic-title">{row['title']}</div>
                    <div class="info-bar">
                        <span>🔥 {row['count']} 次露出</span>
                        <span>📅 最新日期：{row['date']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with st.expander("查看來源細節"):
                seen = set()
                for l, m in zip(row['link'], row['clean_media']):
                    if l not in seen:
                        st.write(f"**[{m}]** ➔ [閱讀原文]({l})")
                        seen.add(l)

except Exception as e:
    st.error(f"連線更新中...")
