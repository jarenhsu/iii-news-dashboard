import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ... (保留原本的 CSS 和頁面設定) ...

try:
    raw_df = pd.read_csv(csv_url)
    
    # 1. 轉換日期格式 (假設日期在第 1 欄或名為 'Timestamp')
    # 如果你的日期欄位名稱不同，請修改下面的 'Timestamp'
    date_col = raw_df.columns[0] 
    raw_df[date_col] = pd.to_datetime(raw_df[date_col])
    
    # 2. 篩選過去 7 天的資料
    seven_days_ago = datetime.now() - timedelta(days=7)
    df = raw_df[raw_df[date_col] >= seven_days_ago]
    
    # 3. 排除空標題並統計熱度
    df = df.dropna(subset=[df.columns[2]])
    col_title = df.columns[2]
    col_link = df.columns[3]
    
    hot_counts = df[col_title].value_counts().reset_index()
    hot_counts.columns = [col_title, 'count']

    st.markdown(f"<p style='text-align: center;'>🗓️ 統計區間：{seven_days_ago.strftime('%Y/%m/%d')} - 至今</p>", unsafe_allow_html=True)
    
    # ... (保留原本的卡片顯示迴圈) ...

except Exception as e:
    st.error("目前尚無過去 7 天的輿情資料。")
