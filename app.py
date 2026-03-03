import streamlit as st
import pandas as pd

# ... (樣式設定維持不變)

try:
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("")

    # 強制依照試算表位置對位
    df['c_title'] = df.iloc[:, 1].astype(str).str.strip()  # B欄
    df['c_date'] = df.iloc[:, 2].astype(str).str.strip()   # C欄
    df['c_link'] = df.iloc[:, 3].astype(str).str.strip()   # D欄
    df['c_media'] = df.iloc[:, 5].astype(str).str.strip()  # F欄

    # 💡 排除無效資料：過濾「未知標題」與「媒體報導」
    df = df[df['c_title'].str.len() > 5]
    df = df[~df['c_title'].str.contains("未知標題|媒體報導|Timestamp")]

    # 聚合與排序
    grouped = df.groupby('c_title').agg({'c_link': list, 'c_media': list, 'c_date': 'max'}).reset_index()
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(20)

    # ... (顯示內容)
