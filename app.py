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
        background-color: #fffbeb; padding: 18px; border-radius: 10px;
        border: 1px solid #fde68a; margin-bottom: 20px;
    }
    .comment-box {
        background-color: #f0f4f8; padding: 15px; border-radius: 8px;
        border-left: 5px solid #af946d; margin-bottom: 10px;
    }
    .rank-text { color: #af946d; font-weight: 900; font-size: 1.5em; margin-bottom: 5px; }
    .topic-title { font-size: 1.3em; font-weight: 700; color: #2c3e50; margin-bottom: 15px; line-height: 1.5; }
    .info-bar { margin-bottom: 15px; font-size: 0.85em; color: #95a5a6; display: flex; gap: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center; padding:10px;'><h1 style='color:#263238;'>📡 資策會輿情熱度觀測站</h1></div>", unsafe_allow_html=True)

# 💡 計算觀測日期
today = datetime.now()
start_date = today - timedelta(days=7)
st.markdown(f'<div style="text-align:center; color:#7f8c8d; margin-bottom:20px;">📅 觀測區間：{start_date.strftime("%Y-%m-%d")} 至 {today.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 📊 輿情資料讀取與預處理
# ---------------------------------------------------------
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df_raw = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")
    # 排除 find.org.tw
    mask = df_raw.apply(lambda row: row.astype(str).str.contains('find.org.tw', case=False).any(), axis=1)
    df = df_raw[~mask].copy()
    
    df['title'] = df.iloc[:, 1].astype(str).str.strip()
    df['date_str'] = df.iloc[:, 2].astype(str).str.strip()
    df['dt'] = pd.to_datetime(df['date_str'], errors='coerce')
    
    # 篩選最近 7 天並統計
    df_7d = df[df['dt'] >= (today - timedelta(days=7))].copy()
    grouped = df_7d.groupby('title').size().reset_index(name='count')
    top_news = grouped.sort_values(by='count', ascending=False).head(3)

    # ---------------------------------------------------------
    # 🤖 AI 自動生成評論 (模擬 AI 觀測員)
    # ---------------------------------------------------------
    if not top_news.empty:
        st.markdown('<div class="ai-box">✨ <strong>AI 輿情觀測員：</strong>', unsafe_allow_html=True)
        
        # 建立分析簡報文字
        focus_topics = "、".join(top_news['title'].tolist())
        ai_comment = f"本週輿情焦點集中於「{focus_topics}」。其中最受關注的話題報導次數達 {top_news.iloc[0]['count']} 次，顯示資策會在數位轉型與技術認證領域的動態持續受到媒體高度重視。"
        
        st.write(ai_comment)
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 📢 同仁觀點布告欄
    # ---------------------------------------------------------
    COMMENT_ID = "1WB4Qqf1lnjvmoq2mIkyasBPib9TzT7Ll27AVjI88Muk"
    comment_url = f"https://docs.google.com/spreadsheets/d/{COMMENT_ID}/export?format=csv"
    try:
        c_df = pd.read_csv(comment_url).tail(3).iloc[::-1]
        if not c_df.empty:
            st.markdown("### 📢 同仁評論")
            for _, row in c_df.iterrows():
                st.markdown(f'<div class="comment-box"><strong>{row.iloc[1]}：</strong> {row.iloc[2]}</div>', unsafe_allow_html=True)
    except:
        pass

    st.markdown("---")

    # ---------------------------------------------------------
    # 🔥 排行榜顯示 (其餘邏輯不變)
    # ---------------------------------------------------------
    # ... (此處保留原本的排行榜卡片渲染代碼)
    st.markdown("### 🔥 本週熱門輿情排行榜")
    # ... (依序顯示 TOP 新聞)

except Exception as e:
    st.error("系統讀取中...")
