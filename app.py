import streamlit as st
import pandas as pd

st.set_page_config(page_title="資策會新聞觀測站", layout="centered")

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("媒體報導")
    
    # 💡 除錯專用：在網頁最上方顯示抓到的欄位名稱 (看完可刪除)
    # st.write("偵測到的欄位有：", list(df.columns))

    # 強制指定欄位：假設 A(時間), B(日期), C(標題), D(連結), E(媒體)
    # 如果你的媒體在最後一欄，就用 -1
    df['c_title'] = df.iloc[:, 2].astype(str).str.strip()
    df['c_link'] = df.iloc[:, 3].astype(str).str.strip()
    df['c_media'] = df.iloc[:, 4].astype(str).str.strip() if df.shape[1] >= 5 else "媒體報導"
    df['c_date'] = df.iloc[:, 1].astype(str).str.strip()

    # 聚合與顯示邏輯 (與之前相同...)
    # ...
    grouped = df.groupby('c_title').agg({'c_link': list, 'c_media': list, 'c_date': 'max'}).reset_index()
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    for i, (_, row) in enumerate(grouped.iterrows()):
        st.subheader(f"RANK #{i+1}: {row['c_title']}")
        st.write(f"📅 日期：{row['c_date']} | 🔥 熱度：{row['count']}")
        with st.expander("查看來源列表"):
            for m, l in zip(row['c_media'], row['c_link']):
                st.markdown(f"**[{m}]** ➔ [閱讀原文]({l})")

except Exception as e:
    st.error(f"錯誤原因：{e}")
