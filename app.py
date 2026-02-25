import streamlit as st
import pandas as pd

# 1. 頁面風格設定
st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

st.markdown("""
    <style>
    .news-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        border: 1px solid #e0e0e0; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .rank-tag { color: #8d6e63; font-weight: bold; font-size: 0.9em; margin-bottom: 5px; }
    .hot-badge { background-color: #f5f5f5; color: #616161; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; }
    a { text-decoration: none !important; color: #2c3e50 !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #4e342e;'>📡 資策會輿情熱度觀測站</h2>", unsafe_allow_html=True)

# 2. 數據處理
SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(csv_url)
    
    if df.empty:
        st.warning("⚠️ 試算表中目前沒有資料，請執行 n8n 流程。")
    else:
        # 💡 自動偵測欄位邏輯
        # 找包含 'http' 的是連結欄位，最長字串的通常是標題欄位
        col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), df.columns[-1])
        col_title = next((c for c in df.columns if '標題' in c or 'Title' in c), None)
        
        # 如果還是找不到標題欄位，就選除了連結以外，內容最長的那一欄
        if not col_title:
            col_title = df.drop(columns=[col_link]).apply(lambda x: x.astype(str).str.len().mean()).idxmax()

        # 統計熱度
        hot_counts = df[col_title].value_counts().reset_index()
        hot_counts.columns = [col_title, 'count']

        st.success(f"✅ 已成功分析 {len(df)} 筆輿情資料")

        # 3. 顯示卡片清單
        for i, (_, row) in enumerate(hot_counts.head(15).iterrows()):
            title = row[col_title]
            count = row['count']
            link = df[df[col_title] == title][col_link].values[0]
            
            medal = "🏆 " if i == 0 else "🥈 " if i == 1 else "🥉 " if i == 2 else f"NO.{i+1} "
            
            st.markdown(f"""
                <div class="news-card">
                    <div class="rank-tag">{medal} TOP TRENDING</div>
                    <a href="{link}" target="_blank"><h3>{title}</h3></a>
                    <span class="hot-badge">📊 媒體露出次數：{count} 次</span>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ 讀取發生錯誤。請確認試算表格式。錯誤訊息: {e}")
