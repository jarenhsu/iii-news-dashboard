import streamlit as st
import pandas as pd

# 儀表板標題設定
st.set_page_config(page_title="資策會新聞觀測站", layout="wide")
st.title("🛡️ 資策會每周新聞觀測系統")

# --- 讀取資料 ---
# 請將下方的網址替換成你 Google 表單連動的那張試算表的「共用網址」
# 記得試算表要開啟「知道連結的人都能查看」
sheet_url = "你的GoogleSheets網址"
csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv")

try:
    df = pd.read_csv(csv_url)
    
    # 建立統計數據
    st.metric("本週追蹤新聞總數", len(df))

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("📌 各部門曝光佔比")
        # 這裡會讀取你在 n8n 分類好的 'department'
        if 'department' in df.columns:
            st.pie_chart(df['department'].value_counts())
            
    with col2:
        st.subheader("📰 最新新聞清單")
        st.dataframe(df[['date', 'title', 'department']], use_container_width=True)

except:
    st.warning("目前還沒抓到資料，請確認 Google Sheets 網址是否正確。")
