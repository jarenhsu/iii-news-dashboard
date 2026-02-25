import streamlit as st
import pandas as pd

st.set_page_config(page_title="資策會新聞熱度排行", layout="wide")
st.title("📡 本週輿情熱度觀測 (Top 5)")

# 試算表 CSV 連結
SHEET_ID = "1rKEVpW2Mx-ZOu6591hyvG_XuKUJnT1kTNuCASc7ewck"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # 讀取資料
    df = pd.read_csv(csv_url)
    
    # 計算標題熱度 (統計第 3 欄 - 標題)
    col_title = df.columns[2]
    hot_counts = df[col_title].value_counts().reset_index()
    hot_counts.columns = [col_title, '次數']
    
    # 取得前五名並合併連結與圖片
    top_5 = pd.merge(hot_counts.head(5), df, on=col_title, how='left').drop_duplicates(subset=[col_title])

    for i, (_, row) in enumerate(top_5.iterrows()):
        with st.container(border=True):
            st.markdown(f"### 第 {i+1} 名 (報導家數：{row['次數']})")
            # 顯示圖片 (讀取最後一欄 image)
            st.image(row.iloc[-1], use_container_width=True)
            st.write(f"**{row[col_title]}**")
            st.link_button("🔗 查看新聞來源", row.iloc[3], use_container_width=True)

except Exception as e:
    st.error("資料更新中，請確認 Google Sheets 已有 image 欄位內容。")
