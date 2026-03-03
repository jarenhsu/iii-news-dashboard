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

# 💡 核心修正：媒體名稱辨識與補位系統
def get_clean_media(raw_m, url):
    # 第一步：檢查試算表 F 欄是否有填寫中文名稱
    clean_m = str(raw_m).strip()
    bad_words = ["媒體", "NEWS", "GOOGLE", "解析", "提取", "UNKNOWN", "[]", "網路媒體"]
    if len(clean_m) > 1 and not any(x in clean_m.upper() for x in bad_words):
        return clean_m

    # 第二步：如果 F 欄無效，則嘗試從網域對照表補齊
    mapping = {
        "yahoo": "Yahoo新聞", "udn": "聯合新聞網", "ltn": "自由時報", "chinatimes": "中時新聞網",
        "ettoday": "ETtoday", "storm": "風傳媒", "cna": "中央社", "setn": "三立新聞",
        "tvbs": "TVBS", "rti.org.tw": "央廣 RTI", "iii.org.tw": "資策會官網", "money.udn": "經濟日報"
    }
    domain = urlparse(str(url)).netloc.lower()
    for key, name in mapping.items():
        if key in domain: return name
        
    # 第三步：最後保險機制，顯示網域大寫
    parts = domain.replace("www.", "").split('.')
    return parts[0].upper() if parts else "網路媒體"

try:
    # 2. 讀取與排除 find.org.tw
    df_raw = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")
    mask = df_raw.apply(lambda row: row.astype(str).str.contains('find.org.tw', case=False).any(), axis=1)
    df = df_raw[~mask].copy()

    # 3. 欄位精準對位
    # B(1):標題, C(2):日期, D(3):連結, F(5):媒體
    df['title'] = df.iloc[:, 1].astype(str).str.strip()
    df['date'] = df.iloc[:, 2].astype(str).str.strip()
    df['link'] = df.iloc[:, 3].astype(str).str.strip()
    df['raw_media'] = df.iloc[:, 5].astype(str).str.strip() # 強制讀取第 6 欄媒體中文名

    # 4. 數據清洗
    df = df[df['title'].str.len() > 5]
    df = df[~df['title'].str.contains("解析失敗|提取中|未知標題")]
    
    # 💡 預先將每一列的媒體名稱處理好
    df['clean_media'] = df.apply(lambda x: get_clean_media(x['raw_media'], x['link']), axis=1)

    # 📊 5. 媒體分佈圖
    st.markdown("### 📊 外部媒體曝光分佈")
    media_counts = df['clean_media'].value_counts().reset_index()
    media_counts.columns = ['媒體名稱', '報導次數']
    st.altair_chart(alt.Chart(media_counts.head(10)).mark_bar().encode(
        x='報導次數:Q', y=alt.Y('媒體名稱:N', sort='-x'), color='報導次數:Q'
    ).properties(height=300), use_container_width=True)

    st.markdown("---")

    # 6. 熱門輿情排行榜
    grouped = df.groupby('title').agg({'link': list, 'clean_media': list, 'date': 'max'}).reset_index()
    grouped['count'] = grouped['link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    if grouped.empty:
        st.info("💡 資料同步中...")
    else:
        st.markdown("### 🔥 熱門輿情排行榜")
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
            with st.expander("📂 查看詳細來源細節"):
                seen = set()
                # 💡 這裡直接使用處理好的 clean_media 列表
                for l, m in zip(row['link'], row['clean_media']):
                    if l not in seen:
                        st.write(f"**[{m}]** ➔ [閱讀原文]({l})")
                        seen.add(l)

except Exception as e:
    st.error(f"系統連線中...")
