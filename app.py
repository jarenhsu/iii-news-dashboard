import streamlit as st
import pandas as pd

# ... (樣式設定維持不變)

try:
    df = pd.read_csv(csv_url, on_bad_lines='skip', engine='python').fillna("未提供")

    # 1. 智慧對位：找到包含 http 的是連結，剩下的長字串是標題
    col_link = next((c for c in df.columns if df[c].astype(str).str.contains('http').any()), None)
    col_date = next((c for c in df.columns if df[c].astype(str).str.match(r'\d{4}').any()), None)
    
    # 排除日期、連結、Timestamp 後，字數最長的是標題
    other_cols = [c for c in df.columns if c != col_link and c != col_date and not df[c].astype(str).str.contains('午').any()]
    col_title = df[other_cols].apply(lambda x: x.astype(str).str.len().mean()).idxmax()
    
    # 媒體名稱則是剩下的那一欄
    col_media = next((c for c in other_cols if c != col_title), None)

    df['c_title'] = df[col_title].astype(str).str.strip()
    df['c_link'] = df[col_link].astype(str).str.strip()
    df['c_media'] = df[col_media].astype(str).str.strip() if col_media else "媒體報導"
    df['c_date'] = df[col_date].astype(str).str.strip() if col_date else "近期"

    # 💡 修正聚合邏輯：避免因為標題微小差異或完全相同導致只剩一筆
    # 我們依照「連結」來確保每一則新聞都是獨特的
    df = df.drop_duplicates(subset=['c_link']) 
    
    # 重新依照標題分組計算熱度
    grouped = df.groupby('c_title').agg({
        'c_link': list, 
        'c_media': list, 
        'c_date': 'max'
    }).reset_index()
    
    grouped['count'] = grouped['c_link'].apply(len)
    grouped = grouped.sort_values(by='count', ascending=False).head(20)

    # ... (顯示卡片邏輯)
