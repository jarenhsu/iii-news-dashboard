import streamlit as st
import pandas as pd

# 1. 頁面風格設定
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcf9; color: #37474f; }
    .news-card {
        background-color: #ffffff; padding: 28px; border-radius: 12px;
        border: 1px solid #f0f0ed; margin-bottom: 22px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }
    .main-title { text-align: center; color: #263238; font-weight: 800; font-size: 2.2em; margin-top: 20px; }
    .sub-title { text-align: center; color: #90a4ae; font-size: 0.95em; margin-bottom: 40px; }
    .rank-text { color: #af946d; font-weight: 900; font-size: 1.6em; margin-bottom: 10px; }
    .news-title { font-size: 1.4em; font-weight: 700; color: #2c3e50; margin: 10px 0; line-height: 1.5; }
    .source-container { margin-top: 20px; padding-top: 15px; border-top: 1px solid #f1f1f1; }
    .source-btn {
        display: inline-block; background-color: #f4f6f7; color: #566573 !important;
        padding: 7px 16px; border-radius: 6px; font-size: 0.85em;
        margin: 5px; border: 1px solid #d5dbdb; text-decoration: none; 
    }
    .info-label { color: #95a5a6; font-size: 0.85em; font-weight: 600; margin-right: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-title'>📡 資策會輿情熱度觀測站</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>WEEKLY TRENDING REPORT</div>", unsafe_allow_html=True)

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取 CSV
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python')

    # --- 智慧自動對位欄位 ---
    # 1. 找連結欄 (包含 http 的那一欄)
    col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), df.columns[-1])
    
    # 2. 找日期欄 (標題包含「日期」或「Time」)
    col_date = next((c for c in df.columns if '日期' in str(c) or 'Date' in str(c) or 'Time' in str(c)), None)
    
    # 3. 找標題欄 (標題包含「標題」或排除日期與連結後最長的那一欄)
    col_title = next((c for c in df.columns if '標題' in str(c) or 'Title' in str(c)), None)
    if not col_title:
        # 如果找不到叫「標題」的，就找剩下的欄位中字數最長的那一欄
        remaining_cols = [c for c in df.columns if c != col_link and c != col_date]
        col_title = df[remaining_cols].apply(lambda x: x.astype(str).str.len().mean()).idxmax()

    # --- 清洗數據 ---
    df['clean_date'] = df[col_date].fillna("近期").astype(str).str.strip() if col_date else "近期"
    df['clean_title'] = df[col_title].fillna("未知標題").astype(str).str.replace(r'\n', '', regex=True).str.strip()
    df['clean_link'] = df[col_link].fillna("").astype(str).str.strip()

    # 排除標頭雜訊
    df = df[df['clean_title'].str.len() > 2]
    df = df[~df['clean_title'].str.contains("新聞標題|標題")]

    # 聚合：同標題的歸類在一起，日期取最新，連結變清單
    agg_dict = {'clean_link': list}
    if col_date:
        agg_dict['clean_date'] = 'max'
    
    grouped = df.groupby('clean_title').agg(agg_dict).reset_index()
    grouped['count'] = grouped['clean_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    # --- 顯示卡片 ---
    if grouped.empty:
        st.info("💡 目前資料同步中，請確認試算表內容。")
    else:
        for i, (_, row) in enumerate(grouped.iterrows()):
            title = row['clean_title']
            links = row['clean_link']
            count = row['count']
            latest_date = row['clean_date'] if col_date else "近期"
            
            medal = "🥇 CHAMPION" if i == 0 else "🥈 SILVER" if i == 1 else "🥉 BRONZE" if i == 2 else f"TOP {i+1}"
            
            # 來源按鈕 (去重處理)
            unique_links = list(dict.fromkeys([u for u in links if 'http' in str(u)]))
            links_html = "".join([f'<a class="source-btn" href="{u}" target="_blank">來源 {idx+1}</a>' for idx, u in enumerate(unique_links)])
            
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-text">{medal}</div>
                    <div class="news-title">{title}</div>
                    <div style="margin-bottom: 15px;">
                        <span class="info-label">📅 最新日期：{latest_date}</span>
                        <span class="info-label">📈 本週熱度：{count} 次報導</span>
                    </div>
                    <div class="source-container">
                        <div style="color: #bdc3c7; font-size: 0.8em; margin-bottom: 10px;">🔗 相關報導連結：</div>
                        {links_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ 發生錯誤：請確認 Google 試算表欄位。({e})")
