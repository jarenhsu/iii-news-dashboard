import streamlit as st
import pandas as pd
from urllib.parse import urlparse

# 1. 頁面風格設定
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e0e0e; color: #f0f0f0; }
    .news-card {
        background-color: #1a1a1a; padding: 30px; border-radius: 15px;
        border: 1px solid #333; margin-bottom: 25px; 
    }
    .main-title { text-align: center; color: #fff; font-weight: 900; font-size: 2.2em; margin-top: 20px; }
    .sub-title { text-align: center; color: #d4af37; font-size: 1em; margin-bottom: 40px; letter-spacing: 2px; }
    .rank-text { color: #d4af37; font-weight: 900; font-size: 1.8em; margin-bottom: 10px; }
    .news-title { font-size: 1.5em; font-weight: 700; color: #fff; margin: 10px 0; line-height: 1.4; }
    .source-container { margin-top: 20px; padding-top: 15px; border-top: 1px dashed #444; }
    .source-btn {
        display: inline-block; background-color: #2c2c2c; color: #d4af37 !important;
        padding: 6px 14px; border-radius: 20px; font-size: 0.85em;
        margin: 5px; border: 1px solid #d4af37; text-decoration: none;
    }
    .source-btn:hover { background-color: #d4af37; color: #000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 媒體名稱轉換
def get_media_label(url):
    if not isinstance(url, str) or "google" in url: return "媒體報導"
    mapping = {
        "yahoo": "Yahoo新聞", "udn": "聯合新聞", "ltn": "自由時報", "chinatimes": "中時",
        "ettoday": "ETtoday", "storm": "風傳媒", "cna": "中央社", "setn": "三立新聞",
        "tvbs": "TVBS", "find.org.tw": "FIND中心", "iii.org.tw": "資策會官網"
    }
    domain = urlparse(url).netloc.lower()
    for key, name in mapping.items():
        if key in domain: return name
    return "相關報導"

st.markdown("<div class='main-title'>📡 資策會輿情熱度觀測站</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>WEEKLY TRENDING REPORT</div>", unsafe_allow_html=True)

# 2. 數據處理 (你的最新試算表 ID)
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 💡 修正：使用具名的欄位標頭，並清理多餘換行
    df = pd.read_csv(csv_url)
    
    # 根據你的表單後台截圖，指定正確的欄位名稱
    # 如果試算表第一列名稱有變動，請以此為準
    col_name_title = "新聞標題"
    col_name_link = "新聞連結"
    
    # 清洗資料
    df[col_name_title] = df[col_name_title].fillna("未知標題").astype(str).str.replace(r'\n', '', regex=True).str.strip()
    df[col_name_link] = df[col_name_link].fillna("").astype(str).str.strip()

    # 過濾掉欄位標頭本身
    df = df[df[col_name_title] != "新聞標題"]

    # 聚合資料
    grouped = df.groupby(col_name_title)[col_name_link].apply(list).reset_index()
    grouped['count'] = grouped[col_name_link].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    # 3. 顯示卡片
    if grouped.empty:
        st.info("目前試算表中沒有符合格式的資料。")
    else:
        for i, (_, row) in enumerate(grouped.iterrows()):
            title = row[col_name_title]
            links = row[col_name_link]
            count = row['count']
            
            medal = "🥇 CHAMPION" if i == 0 else "🥈 SILVER" if i == 1 else "🥉 BRONZE" if i == 2 else f"TOP {i+1}"
            links_html = "".join([f'<a class="source-btn" href="{u}" target="_blank">🌐 {get_media_label(u)}</a>' for u in links if u and 'http' in u])
            
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-text">{medal}</div>
                    <div class="news-title">{title}</div>
                    <div style="color: #d4af37; font-weight: bold; margin-bottom: 10px;">🔥 本週熱度：{count} 次報導</div>
                    <div class="source-container">
                        <div style="color: #888; font-size: 0.8em; margin-bottom: 10px;">🔗 媒體來源：</div>
                        {links_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    # 如果報錯，至少顯示錯誤訊息讓我們除錯
    st.error(f"系統資料解析異常。請確保試算表欄位名稱為『新聞標題』與『新聞連結』。")
