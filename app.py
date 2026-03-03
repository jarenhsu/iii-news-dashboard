import streamlit as st
import pandas as pd

# 1. 樣式設定
st.set_page_config(page_title="資策會輿情熱度觀測站", layout="centered")
st.markdown("<style>.news-card { background: white; padding: 20px; border-radius: 10px; border: 1px solid #eee; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }</style>", unsafe_allow_html=True)
st.title("📡 資策會輿情熱度觀測站")

SHEET_ID = "1cwFO20QP4EZrl5PYVOjVgevJS2D1VzCUazb9x0fHEoI"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")
    # B標題(1), C日期(2), D連結(3), F媒體(5)
    df['c_title'] = df.iloc[:, 1].astype(str).str.strip()
    df['c_date'] = df.iloc[:, 2].astype(str).str.strip()
    df['c_link'] = df.iloc[:, 3].astype(str).str.strip()
    df['c_media'] = df.iloc[:, 5].astype(str).str.strip()

    # 過濾解析失敗的髒資料
    df = df[df['c_title'].str.len() > 5]
    df = df[~df['c_title'].str.contains("解析失敗|提取中|未知標題")]

    grouped = df.groupby('c_title').agg({'c_link': list, 'c_media': list, 'c_date': 'max'}).reset_index()
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(15)

    if grouped.empty:
        st.info("💡 資料同步中，請執行 n8n 寫入正確標題。")
    else:
        for i, (_, row) in enumerate(grouped.iterrows()):
            st.markdown(f'<div class="news-card"><h4>TOP {i+1}: {row["c_title"]}</h4><p>🔥 {row["count"]} 次報導 ｜ 📅 {row["c_date"]}</p></div>', unsafe_allow_html=True)
            with st.expander("查看來源細節"):
                for m, l in zip(row['c_media'], row['c_link']):
                    st.write(f"**[{m}]** ➔ [閱讀原文]({l})")

# 💡 關鍵補完：解決 SyntaxError
except Exception as e:
    st.error(f"解析發生異常：{e}")
