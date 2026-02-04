# 🌏 イオン 地域別業績分析ダッシュボード（四半期）

イオン株式会社のグローバル地域別セグメント業績（四半期別）を可視化・分析するStreamlitダッシュボードアプリケーションです。

## 📊 機能概要

| タブ | 内容 |
|------|------|
| **📊 全体概要** | 地域別営業収益・営業利益の積み上げ棒グラフ（四半期） |
| **📈 構成比推移** | 営業収益構成比（エリアチャート）・営業利益構成比（積み上げ棒グラフ） |
| **💹 利益率推移** | 地域別営業利益率の折れ線グラフ |
| **🚀 前年同期比** | 営業収益・営業利益の前年同期比成長率 |
| **📅 季節性分析** | Q1〜Q4の四半期別平均値分析 |
| **🔍 地域詳細** | 選択した地域の4分割詳細チャート |

## 🗺️ 対象地域

- 🇯🇵 **日本**（青）
- 🇨🇳 **中国**（赤）
- 🌏 **アセアン**（緑）
- 🌐 **その他**（グレー）

## 🆕 四半期版の特徴

1. **表示範囲の選択**
   - 「直近N四半期」モード：スライダーで表示四半期数を選択
   - 「年度指定」モード：特定年度の四半期のみ表示

2. **前年同期比分析**
   - 4四半期前との比較による成長率を算出
   - 営業収益・営業利益両方の前年同期比を表示

3. **季節性分析**
   - Q1〜Q4の四半期別平均値を地域別に比較
   - 季節的なパターンの把握が可能

## 📁 ディレクトリ構成

```
aeon_region_quarterly_dashboard/
├── app.py                 # メインアプリケーション
├── requirements.txt       # Python依存パッケージ
├── packages.txt           # システムパッケージ（Streamlit Cloud用）
├── README.md              # このファイル
├── .gitignore             # Git除外設定
├── data/
│   └── region_data.xlsx   # 地域別業績データ（四半期）
└── fonts/
    └── ipaexg.ttf         # 日本語フォント（IPAexゴシック）
```

## 🚀 セットアップ

### ローカル環境での実行

1. リポジトリをクローン
```bash
git clone https://github.com/YOUR_USERNAME/aeon_region_quarterly_dashboard.git
cd aeon_region_quarterly_dashboard
```

2. 依存パッケージをインストール
```bash
pip install -r requirements.txt
```

3. アプリを起動
```bash
streamlit run app.py
```

4. ブラウザで `http://localhost:8501` にアクセス

### Streamlit Cloudでのデプロイ

1. このリポジトリをGitHubにプッシュ
2. [Streamlit Cloud](https://streamlit.io/cloud) にアクセス
3. 「New app」をクリック
4. リポジトリ、ブランチ、`app.py` を選択
5. 「Deploy」をクリック

## 📈 データ形式

`data/region_data.xlsx` には以下のカラムが含まれています：

| カラム名 | 説明 |
|---------|------|
| 地域 | 日本、中国、アセアン、その他 |
| 決算年度 | FY2018-1Q〜FY2025-3Q（四半期形式） |
| 決算種別 | Q1, Q2, Q3, Q4 |
| 営業収益 | 百万円 |
| 営業利益 | 百万円 |
| 営業収益営業利益率 | % |
| 営業収益構成比 | % |
| 営業利益構成比 | % |

## 📥 レポート出力

各タブで「📥 HTMLでダウンロード」ボタンをクリックすると、チャートとテーブルを含むHTMLレポートをダウンロードできます。

## 🛠️ 技術スタック

- **Python** 3.9+
- **Streamlit** - Webアプリケーションフレームワーク
- **Pandas** - データ処理
- **Matplotlib** - グラフ描画
- **Seaborn** - 統計データ可視化
- **OpenPyXL** - Excelファイル読み込み

## 📝 ライセンス

このプロジェクトは教育・分析目的で作成されています。

## 🔗 関連リンク

- [イオン株式会社 IR情報](https://www.aeon.info/ir/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

📊 Powered by Streamlit
