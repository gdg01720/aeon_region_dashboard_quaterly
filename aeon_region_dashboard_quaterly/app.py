import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import os
import io
import base64

# --- 1. 日本語フォント設定 (ローカル & Cloud 両対応) ---
def setup_font():
    """fontsフォルダからフォントを読み込み、日本語表示を有効化"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_dir, "fonts", "ipaexg.ttf")
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = prop.get_name()
        return prop.get_name()
    else:
        # フォールバック: システムフォントを試行
        plt.rcParams['font.family'] = ['Meiryo', 'MS Gothic', 'Hiragino Sans', 'sans-serif']
        return 'sans-serif'

font_name = setup_font()
plt.rcParams['axes.unicode_minus'] = False  # マイナス記号の文字化け対策
sns.set_theme(style="whitegrid", rc={"font.family": font_name})

st.set_page_config(page_title="イオン 地域別業績分析ダッシュボード（四半期）", layout="wide")

# --- 2. ユーティリティ関数 ---
def get_html_report(df, title, fig=None):
    """HTMLダウンロード用データの生成（テーブル＋チャート）"""
    chart_html = ""
    if fig is not None:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        chart_html = f'<div style="text-align:center; margin: 20px 0;"><img src="data:image/png;base64,{img_base64}" style="max-width:100%;"/></div>'
    
    return f"""
    <html><head><meta charset='utf-8'>
    <style>
        body {{ font-family: 'Hiragino Sans', 'Meiryo', sans-serif; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; background: white; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: right; }}
        th {{ background: linear-gradient(135deg, #1f77b4, #ff7f0e); color: white; text-align: center; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        tr:hover {{ background-color: #f0f0f0; }}
        h2 {{ color: #2C3E50; border-left: 5px solid #1f77b4; padding-left: 15px; margin-top: 0; }}
        .timestamp {{ color: #888; font-size: 12px; text-align: right; margin-top: 20px; }}
    </style></head>
    <body>
    <div class="container">
        <h2>📊 {title}</h2>
        {chart_html}
        <h3>📋 詳細データ</h3>
        {df.to_html(classes='data-table')}
        <p class="timestamp">生成日時: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    </body></html>
    """

def sort_quarter_key(q):
    """四半期のソートキーを生成（例: FY2023-1Q → 20231）"""
    parts = q.replace('FY', '').replace('Q', '').split('-')
    return int(parts[0]) * 10 + int(parts[1])

# --- 3. データの読み込み ---
def convert_to_numeric(series):
    """カンマ区切り文字列を数値に変換"""
    if series.dtype == 'object':
        return pd.to_numeric(
            series.astype(str).str.replace(',', '').str.strip(),
            errors='coerce'
        ).fillna(0)
    return series

@st.cache_data
def load_region_data():
    """地域別データの読み込み（四半期）"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "data", "region_data.xlsx")
    if os.path.exists(path):
        df = pd.read_excel(path)
        
        # 決算種別がQ1, Q2, Q3, Q4のデータのみを抽出
        df = df[df['決算種別'].isin(['Q1', 'Q2', 'Q3', 'Q4'])].reset_index(drop=True)
        
        # 数値カラムの変換（必要に応じて）
        numeric_cols = ['営業収益', '営業利益', '営業収益営業利益率', '営業収益構成比', '営業利益構成比']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = convert_to_numeric(df[col])
        
        # 四半期ソート用の数値列を追加（FY2023-1Q → 20231）
        df['四半期数値'] = df['決算年度'].apply(sort_quarter_key)
        df = df.sort_values(['地域', '四半期数値']).reset_index(drop=True)
        
        # 年度と四半期を分割
        df['年度'] = df['決算年度'].str.extract(r'(FY\d{4})')[0]
        df['四半期'] = df['決算種別']
        
        return df
    return None

# --- 4. メイン UI ---
st.title("🌏 イオン 地域別業績分析ダッシュボード（四半期）")

df_raw = load_region_data()

if df_raw is not None:
    # --- サイドバー ---
    st.sidebar.header("🔧 分析条件")
    
    # 四半期リスト取得（ソート済み）
    raw_quarters = sorted(df_raw['決算年度'].unique(), key=sort_quarter_key)
    
    # 年度リスト取得
    fiscal_years = sorted(df_raw['年度'].unique(), key=lambda x: int(x.replace('FY', '')))
    
    # 表示範囲選択
    st.sidebar.subheader("表示範囲")
    display_mode = st.sidebar.radio("表示モード", ["直近N四半期", "年度指定"], index=0)
    
    if display_mode == "直近N四半期":
        n_quarters = st.sidebar.slider("表示四半期数", min_value=4, max_value=len(raw_quarters), value=12)
        selected_quarters = raw_quarters[-n_quarters:]
    else:
        selected_years = st.sidebar.multiselect("年度を選択", fiscal_years, default=fiscal_years[-2:])
        selected_quarters = [q for q in raw_quarters if any(q.startswith(y) for y in selected_years)]
    
    # 地域リスト取得（表示順序を固定）
    region_order = ['日本', '中国', 'アセアン', 'その他']
    region_list = [r for r in region_order if r in df_raw['地域'].unique()]
    
    # 地域詳細分析用の選択
    st.sidebar.markdown("---")
    st.sidebar.subheader("地域詳細分析")
    selected_region = st.sidebar.selectbox("地域を選択", region_list)

    # --- タブ構成 ---
    tab_overview, tab_composition, tab_margin, tab_yoy, tab_seasonal, tab_detail = st.tabs([
        "📊 全体概要", "📈 構成比推移", "💹 利益率推移", "🚀 前年同期比", "📅 季節性分析", "🔍 地域詳細"
    ])

    # --- 色パレット定義 ---
    region_colors = {
        '日本': '#1f77b4',      # 青
        '中国': '#d62728',      # 赤
        'アセアン': '#2ca02c',  # 緑
        'その他': '#7f7f7f'     # グレー
    }

    # 表示用データのフィルタリング
    df_filtered = df_raw[df_raw['決算年度'].isin(selected_quarters)].copy()

    # ==========================================================
    # タブ1: 全体概要
    # ==========================================================
    with tab_overview:
        st.subheader("地域別収益・利益の推移（四半期）")
        
        # 営業収益の積み上げ棒グラフ
        pivot_revenue = df_filtered.pivot_table(
            index='決算年度', columns='地域', values='営業収益', aggfunc='sum'
        ).reindex(selected_quarters).reindex(columns=region_list)
        
        fig1, ax1 = plt.subplots(figsize=(14, 6))
        pivot_revenue.plot(kind='bar', stacked=True, ax=ax1, 
                          color=[region_colors.get(r, '#333') for r in pivot_revenue.columns])
        ax1.set_title('地域別営業収益の推移（四半期・積み上げ）', fontsize=14, fontweight='bold')
        ax1.set_xlabel('決算四半期')
        ax1.set_ylabel('営業収益（百万円）')
        ax1.legend(title='地域', bbox_to_anchor=(1.02, 1), loc='upper left')
        ax1.tick_params(axis='x', rotation=45)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
        plt.tight_layout()
        st.pyplot(fig1)
        
        # 営業収益テーブル
        st.markdown("#### 営業収益一覧（百万円）")
        revenue_table = pivot_revenue.T
        st.dataframe(revenue_table.style.format("{:,.0f}"), width='stretch')
        
        html_rev = get_html_report(revenue_table, "地域別営業収益の推移（四半期）", fig1)
        st.download_button("📥 HTMLでダウンロード（チャート＋テーブル）", html_rev, "地域別営業収益レポート_四半期.html", "text/html", key="rev_html")
        
        st.divider()
        
        # 営業利益の積み上げ棒グラフ
        pivot_profit = df_filtered.pivot_table(
            index='決算年度', columns='地域', values='営業利益', aggfunc='sum'
        ).reindex(selected_quarters).reindex(columns=region_list)
        
        fig2, ax2 = plt.subplots(figsize=(14, 6))
        pivot_profit.plot(kind='bar', stacked=True, ax=ax2, 
                         color=[region_colors.get(r, '#333') for r in pivot_profit.columns])
        ax2.set_title('地域別営業利益の推移（四半期・積み上げ）', fontsize=14, fontweight='bold')
        ax2.set_xlabel('決算四半期')
        ax2.set_ylabel('営業利益（百万円）')
        ax2.axhline(y=0, color='black', linewidth=0.5)
        ax2.legend(title='地域', bbox_to_anchor=(1.02, 1), loc='upper left')
        ax2.tick_params(axis='x', rotation=45)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
        plt.tight_layout()
        st.pyplot(fig2)
        
        # 営業利益テーブル
        st.markdown("#### 営業利益一覧（百万円）")
        profit_table = pivot_profit.T
        st.dataframe(profit_table.style.format("{:,.0f}"), width='stretch')
        
        html_profit = get_html_report(profit_table, "地域別営業利益の推移（四半期）", fig2)
        st.download_button("📥 HTMLでダウンロード（チャート＋テーブル）", html_profit, "地域別営業利益レポート_四半期.html", "text/html", key="profit_html")

    # ==========================================================
    # タブ2: 構成比推移
    # ==========================================================
    with tab_composition:
        st.subheader("地域別構成比の推移（四半期）")
        
        # 営業収益構成比 - エリアチャート
        pivot_rev_comp = df_filtered.pivot_table(
            index='決算年度', columns='地域', values='営業収益構成比', aggfunc='sum'
        ).reindex(selected_quarters).reindex(columns=region_list)
        
        fig3, ax3 = plt.subplots(figsize=(14, 6))
        pivot_rev_comp.plot(kind='area', stacked=True, ax=ax3, alpha=0.8,
                           color=[region_colors.get(r, '#333') for r in pivot_rev_comp.columns])
        ax3.set_title('地域別営業収益構成比の推移（四半期）', fontsize=14, fontweight='bold')
        ax3.set_xlabel('決算四半期')
        ax3.set_ylabel('構成比（%）')
        ax3.set_ylim(0, 100)
        ax3.legend(title='地域', bbox_to_anchor=(1.02, 1), loc='upper left')
        ax3.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        st.pyplot(fig3)
        
        st.markdown("#### 営業収益構成比一覧（%）")
        crosstab_rev_comp = pivot_rev_comp.T
        st.dataframe(crosstab_rev_comp.style.format("{:.1f}").bar(subset=crosstab_rev_comp.columns, color='skyblue', vmin=0), 
                     width='stretch')
        
        html_comp1 = get_html_report(crosstab_rev_comp, "営業収益構成比の推移（四半期）", fig3)
        st.download_button("📥 HTMLでダウンロード（チャート＋テーブル）", html_comp1, "営業収益構成比レポート_四半期.html", "text/html", key="comp_rev_html")
        
        st.divider()
        
        # 営業利益構成比 - 積み上げ棒グラフ（正負両方の積み上げに対応）
        pivot_profit_comp = df_filtered.pivot_table(
            index='決算年度', columns='地域', values='営業利益構成比', aggfunc='sum'
        ).reindex(selected_quarters).reindex(columns=region_list)
        
        fig4, ax4 = plt.subplots(figsize=(14, 6))
        pivot_profit_comp.plot(kind='bar', stacked=True, ax=ax4,
                              color=[region_colors.get(r, '#333') for r in pivot_profit_comp.columns])
        ax4.set_title('地域別営業利益構成比の推移（四半期・積み上げ）', fontsize=14, fontweight='bold')
        ax4.set_xlabel('決算四半期')
        ax4.set_ylabel('構成比（%）')
        ax4.axhline(y=0, color='black', linewidth=0.5)
        ax4.legend(title='地域', bbox_to_anchor=(1.02, 1), loc='upper left')
        ax4.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        st.pyplot(fig4)
        
        st.markdown("#### 営業利益構成比一覧（%）")
        crosstab_profit_comp = pivot_profit_comp.T
        st.dataframe(crosstab_profit_comp.style.format("{:.1f}"), width='stretch')
        
        html_comp2 = get_html_report(crosstab_profit_comp, "営業利益構成比の推移（四半期）", fig4)
        st.download_button("📥 HTMLでダウンロード（チャート＋テーブル）", html_comp2, "営業利益構成比レポート_四半期.html", "text/html", key="comp_profit_html")

    # ==========================================================
    # タブ3: 利益率推移
    # ==========================================================
    with tab_margin:
        st.subheader("地域別営業利益率の推移（四半期）")
        
        fig5, ax5 = plt.subplots(figsize=(14, 7))
        for region in region_list:
            reg_data = df_filtered[df_filtered['地域'] == region].sort_values('四半期数値')
            ax5.plot(reg_data['決算年度'], reg_data['営業収益営業利益率'], 
                    marker='o', label=region, color=region_colors.get(region, '#333'), linewidth=2, markersize=4)
        ax5.set_title('地域別営業利益率の推移（四半期）', fontsize=14, fontweight='bold')
        ax5.set_xlabel('決算四半期')
        ax5.set_ylabel('営業利益率（%）')
        ax5.axhline(y=0, color='black', linewidth=0.5)
        ax5.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
        ax5.tick_params(axis='x', rotation=45)
        ax5.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig5)
        
        # 営業利益率テーブル
        st.markdown("#### 営業利益率一覧（%）")
        pivot_margin = df_filtered.pivot_table(
            index='決算年度', columns='地域', values='営業収益営業利益率', aggfunc='sum'
        ).reindex(selected_quarters).reindex(columns=region_list).T
        st.dataframe(pivot_margin.style.format("{:.1f}"), width='stretch')
        
        html_margin = get_html_report(pivot_margin, "地域別営業利益率の推移（四半期）", fig5)
        st.download_button("📥 HTMLでダウンロード（チャート＋テーブル）", html_margin, "営業利益率レポート_四半期.html", "text/html", key="margin_html")

    # ==========================================================
    # タブ4: 前年同期比
    # ==========================================================
    with tab_yoy:
        st.subheader("地域別営業収益 前年同期比成長率")
        
        # 前年同期比を計算
        yoy_df = pd.DataFrame()
        for region in region_list:
            reg_data = df_raw[df_raw['地域'] == region].sort_values('四半期数値').copy()
            # 前年同期（4四半期前）との比較
            reg_data['前年同期比'] = np.round(
                (reg_data['営業収益'] / reg_data['営業収益'].shift(4) - 1) * 100, 1
            )
            yoy_df = pd.concat([yoy_df, reg_data], axis=0)
        
        yoy_df = yoy_df.reset_index(drop=True)
        yoy_filtered = yoy_df[yoy_df['決算年度'].isin(selected_quarters)]
        
        fig6, ax6 = plt.subplots(figsize=(14, 7))
        for region in region_list:
            reg_data = yoy_filtered[yoy_filtered['地域'] == region].sort_values('四半期数値')
            ax6.plot(reg_data['決算年度'], reg_data['前年同期比'], 
                    marker='o', label=region, color=region_colors.get(region, '#333'), linewidth=2, markersize=4)
        ax6.set_title('地域別営業収益 前年同期比成長率', fontsize=14, fontweight='bold')
        ax6.set_xlabel('決算四半期')
        ax6.set_ylabel('成長率（%）')
        ax6.axhline(y=0, color='black', linewidth=0.5, linestyle='--')
        ax6.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
        ax6.tick_params(axis='x', rotation=45)
        ax6.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig6)
        
        # 前年同期比テーブル
        st.markdown("#### 前年同期比成長率一覧（%）")
        pivot_yoy = yoy_filtered.pivot_table(
            index='決算年度', columns='地域', values='前年同期比', aggfunc='sum'
        ).reindex(selected_quarters).reindex(columns=region_list).T
        st.dataframe(pivot_yoy.style.format("{:.1f}"), width='stretch')
        
        html_yoy = get_html_report(pivot_yoy, "地域別営業収益 前年同期比成長率", fig6)
        st.download_button("📥 HTMLでダウンロード（チャート＋テーブル）", html_yoy, "前年同期比レポート.html", "text/html", key="yoy_html")
        
        st.divider()
        
        # 営業利益の前年同期比
        st.subheader("地域別営業利益 前年同期比成長率")
        
        yoy_profit_df = pd.DataFrame()
        for region in region_list:
            reg_data = df_raw[df_raw['地域'] == region].sort_values('四半期数値').copy()
            reg_data['営業利益前年同期比'] = np.round(
                (reg_data['営業利益'] / reg_data['営業利益'].shift(4) - 1) * 100, 1
            )
            yoy_profit_df = pd.concat([yoy_profit_df, reg_data], axis=0)
        
        yoy_profit_df = yoy_profit_df.reset_index(drop=True)
        yoy_profit_filtered = yoy_profit_df[yoy_profit_df['決算年度'].isin(selected_quarters)]
        
        fig7, ax7 = plt.subplots(figsize=(14, 7))
        for region in region_list:
            reg_data = yoy_profit_filtered[yoy_profit_filtered['地域'] == region].sort_values('四半期数値')
            ax7.plot(reg_data['決算年度'], reg_data['営業利益前年同期比'], 
                    marker='o', label=region, color=region_colors.get(region, '#333'), linewidth=2, markersize=4)
        ax7.set_title('地域別営業利益 前年同期比成長率', fontsize=14, fontweight='bold')
        ax7.set_xlabel('決算四半期')
        ax7.set_ylabel('成長率（%）')
        ax7.axhline(y=0, color='black', linewidth=0.5, linestyle='--')
        ax7.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
        ax7.tick_params(axis='x', rotation=45)
        ax7.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig7)
        
        # 営業利益前年同期比テーブル
        st.markdown("#### 営業利益 前年同期比成長率一覧（%）")
        pivot_yoy_profit = yoy_profit_filtered.pivot_table(
            index='決算年度', columns='地域', values='営業利益前年同期比', aggfunc='sum'
        ).reindex(selected_quarters).reindex(columns=region_list).T
        st.dataframe(pivot_yoy_profit.style.format("{:.1f}"), width='stretch')
        
        html_yoy_profit = get_html_report(pivot_yoy_profit, "地域別営業利益 前年同期比成長率", fig7)
        st.download_button("📥 HTMLでダウンロード（チャート＋テーブル）", html_yoy_profit, "営業利益前年同期比レポート.html", "text/html", key="yoy_profit_html")

    # ==========================================================
    # タブ5: 季節性分析
    # ==========================================================
    with tab_seasonal:
        st.subheader("四半期別季節性分析")
        
        # 四半期別の平均を計算
        seasonal_df = df_raw.copy()
        seasonal_df['Q'] = seasonal_df['決算種別']
        
        # 営業収益の四半期別平均（地域別）
        seasonal_rev = seasonal_df.pivot_table(
            index='Q', columns='地域', values='営業収益', aggfunc='mean'
        ).reindex(['Q1', 'Q2', 'Q3', 'Q4']).reindex(columns=region_list)
        
        fig8, ax8 = plt.subplots(figsize=(10, 6))
        x = np.arange(4)
        width = 0.2
        for i, region in enumerate(region_list):
            ax8.bar(x + i * width, seasonal_rev[region], width, 
                   label=region, color=region_colors.get(region, '#333'))
        ax8.set_title('地域別 四半期平均営業収益', fontsize=14, fontweight='bold')
        ax8.set_xlabel('四半期')
        ax8.set_ylabel('平均営業収益（百万円）')
        ax8.set_xticks(x + width * (len(region_list) - 1) / 2)
        ax8.set_xticklabels(['Q1', 'Q2', 'Q3', 'Q4'])
        ax8.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
        ax8.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
        ax8.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        st.pyplot(fig8)
        
        st.markdown("#### 四半期別平均営業収益（百万円）")
        st.dataframe(seasonal_rev.T.style.format("{:,.0f}"), width='stretch')
        
        st.divider()
        
        # 営業利益の四半期別平均（地域別）
        seasonal_profit = seasonal_df.pivot_table(
            index='Q', columns='地域', values='営業利益', aggfunc='mean'
        ).reindex(['Q1', 'Q2', 'Q3', 'Q4']).reindex(columns=region_list)
        
        fig9, ax9 = plt.subplots(figsize=(10, 6))
        for i, region in enumerate(region_list):
            ax9.bar(x + i * width, seasonal_profit[region], width, 
                   label=region, color=region_colors.get(region, '#333'))
        ax9.set_title('地域別 四半期平均営業利益', fontsize=14, fontweight='bold')
        ax9.set_xlabel('四半期')
        ax9.set_ylabel('平均営業利益（百万円）')
        ax9.set_xticks(x + width * (len(region_list) - 1) / 2)
        ax9.set_xticklabels(['Q1', 'Q2', 'Q3', 'Q4'])
        ax9.axhline(y=0, color='black', linewidth=0.5)
        ax9.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
        ax9.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
        ax9.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        st.pyplot(fig9)
        
        st.markdown("#### 四半期別平均営業利益（百万円）")
        st.dataframe(seasonal_profit.T.style.format("{:,.0f}"), width='stretch')
        
        st.divider()
        
        # 営業利益率の四半期別平均（地域別）
        seasonal_margin = seasonal_df.pivot_table(
            index='Q', columns='地域', values='営業収益営業利益率', aggfunc='mean'
        ).reindex(['Q1', 'Q2', 'Q3', 'Q4']).reindex(columns=region_list)
        
        fig10, ax10 = plt.subplots(figsize=(10, 6))
        for region in region_list:
            ax10.plot(['Q1', 'Q2', 'Q3', 'Q4'], seasonal_margin[region], 
                     marker='o', label=region, color=region_colors.get(region, '#333'), linewidth=2)
        ax10.set_title('地域別 四半期平均営業利益率', fontsize=14, fontweight='bold')
        ax10.set_xlabel('四半期')
        ax10.set_ylabel('平均営業利益率（%）')
        ax10.axhline(y=0, color='black', linewidth=0.5)
        ax10.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
        ax10.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig10)
        
        st.markdown("#### 四半期別平均営業利益率（%）")
        st.dataframe(seasonal_margin.T.style.format("{:.1f}"), width='stretch')
        
        html_seasonal = get_html_report(seasonal_margin.T, "四半期別季節性分析", fig10)
        st.download_button("📥 HTMLでダウンロード（チャート＋テーブル）", html_seasonal, "季節性分析レポート.html", "text/html", key="seasonal_html")

    # ==========================================================
    # タブ6: 地域詳細
    # ==========================================================
    with tab_detail:
        st.subheader(f"🔍 {selected_region} - 詳細分析（四半期）")
        
        # 地域データ抽出
        reg_detail = df_filtered[df_filtered['地域'] == selected_region].sort_values('四半期数値').copy()
        
        if not reg_detail.empty:
            # 前年同期比計算
            reg_all = df_raw[df_raw['地域'] == selected_region].sort_values('四半期数値').copy()
            reg_all['前年同期比'] = np.round(
                (reg_all['営業収益'] / reg_all['営業収益'].shift(4) - 1) * 100, 1
            )
            reg_detail = reg_all[reg_all['決算年度'].isin(selected_quarters)].copy()
            
            quarters_display = reg_detail['決算年度'].tolist()
            
            # 2x2サブプロット
            fig11, axs = plt.subplots(2, 2, figsize=(14, 10))
            
            # 営業収益
            axs[0, 0].bar(quarters_display, reg_detail['営業収益'], color=region_colors.get(selected_region, 'skyblue'))
            axs[0, 0].set_title('営業収益', fontsize=12, fontweight='bold')
            axs[0, 0].set_ylabel('金額（百万円）')
            axs[0, 0].tick_params(axis='x', rotation=45)
            axs[0, 0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
            
            # 営業利益
            colors = ['orange' if v >= 0 else 'red' for v in reg_detail['営業利益']]
            axs[0, 1].bar(quarters_display, reg_detail['営業利益'], color=colors)
            axs[0, 1].set_title('営業利益', fontsize=12, fontweight='bold')
            axs[0, 1].set_ylabel('金額（百万円）')
            axs[0, 1].axhline(y=0, color='black', linewidth=0.5)
            axs[0, 1].tick_params(axis='x', rotation=45)
            axs[0, 1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
            
            # 前年同期比成長率
            axs[1, 0].plot(quarters_display, reg_detail['前年同期比'], marker='o', 
                          color=region_colors.get(selected_region, 'green'), linewidth=2)
            axs[1, 0].set_title('営業収益 前年同期比成長率', fontsize=12, fontweight='bold')
            axs[1, 0].set_ylabel('成長率（%）')
            axs[1, 0].axhline(y=0, color='black', linewidth=0.5, linestyle='--')
            axs[1, 0].tick_params(axis='x', rotation=45)
            axs[1, 0].grid(True, alpha=0.3)
            
            # 営業利益率
            axs[1, 1].plot(quarters_display, reg_detail['営業収益営業利益率'], marker='o', color='purple', linewidth=2)
            axs[1, 1].set_title('営業利益率', fontsize=12, fontweight='bold')
            axs[1, 1].set_ylabel('利益率（%）')
            axs[1, 1].axhline(y=0, color='black', linewidth=0.5)
            axs[1, 1].tick_params(axis='x', rotation=45)
            axs[1, 1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig11)
            
            # 詳細テーブル
            st.markdown("#### 業績推移テーブル")
            display_cols = ['決算年度', '営業収益', '営業利益', '前年同期比', '営業収益営業利益率']
            display_df = reg_detail[display_cols].copy()
            display_df = display_df.rename(columns={'営業収益営業利益率': '営業利益率'})
            display_df = display_df.set_index('決算年度')
            
            format_dict = {
                '営業収益': '{:,.0f}',
                '営業利益': '{:,.0f}',
                '前年同期比': '{:.1f}',
                '営業利益率': '{:.1f}'
            }
            st.dataframe(display_df.style.format(format_dict), width='stretch')
            
            # 構成比テーブル（横持ち・バーチャート風スタイル）
            st.markdown("#### 構成比推移")
            comp_df = reg_detail[['決算年度', '営業収益構成比', '営業利益構成比']].copy()
            comp_df = comp_df.set_index('決算年度').T
            
            st.dataframe(
                comp_df.style.format("{:.1f}%").bar(subset=comp_df.columns, color='skyblue', vmin=0),
                width='stretch'
            )
            
            html_content = get_html_report(display_df, f"{selected_region} - 業績推移（四半期）", fig11)
            st.download_button(f"📥 HTMLでダウンロード（チャート＋テーブル）", html_content, f"{selected_region}_詳細レポート_四半期.html", "text/html", key="detail_html")
        
        else:
            st.warning("選択された地域のデータが見つかりません。")

else:
    st.error("データファイルが見つかりません。リポジトリの data/ フォルダを確認してください。")

# --- フッター ---
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; font-size: 12px;">
    🌏 イオン 地域別業績分析ダッシュボード（四半期） | Powered by Streamlit
</div>
""", unsafe_allow_html=True)
