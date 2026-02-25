# ... (前面的 CSS 保持不變) ...

try:
    df = pd.read_csv(csv_url)
    
    if df.empty:
        st.warning("⚠️ 試算表中目前沒有資料。")
    else:
        # 1. 自動尋找包含「標題」和「連結」關鍵字的欄位
        col_title = [c for c in df.columns if '標題' in c][0]
        col_link = [c for c in df.columns if '連結' in c][0]
        
        # 2. 統計熱度
        hot_counts = df[col_title].value_counts().reset_index()
        hot_counts.columns = [col_title, 'count']

        st.success(f"✅ 已成功讀取 {len(df)} 筆輿情資料")

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
