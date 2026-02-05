# 📊 イオン 四半期別セグメント業績分析ダッシュボード

イオン株式会社の四半期別セグメント業績を可視化・分析するStreamlitアプリケーションです。

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🎯 機能

### タブ構成

| タブ | 内容 |
|------|------|
| 📊 全体概要 | セグメント別営業収益・営業利益の積み上げ棒グラフと一覧表 |
| 📈 構成比推移 | 営業収益・営業利益構成比の推移（折れ線グラフ） |
| 💹 利益率推移 | セグメント別営業利益率の推移 |
| 🚀 成長率分析 | 基準四半期からの営業収益成長率比較 |
| 🔍 セグメント詳細 | 選択したセグメントの詳細分析（4象限グラフ+構成比テーブル） |

### 対象セグメント

- GMS事業（総合スーパー）
- SM事業（スーパーマーケット）
- H&W事業（ヘルス＆ウエルネス）
- 総合金融事業
- ディベロッパー事業
- サービス・専門店事業
- 国際事業
- DS事業（ディスカウントストア）
- その他

### 主な機能

- 📅 分析期間の選択（開始〜終了四半期）
- 📈 インタラクティブなチャート表示
- 📥 HTMLレポートダウンロード（チャート＋テーブル）
- 🔄 セグメント選択によるフィルタリング
- 📱 レスポンシブ対応（PC・タブレット・スマートフォン）

## 🚀 セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/YOUR_USERNAME/aeon-segment-quarterly-analysis.git
cd aeon-segment-quarterly-analysis
```

### 2. 仮想環境の作成（推奨）

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. 日本語フォントの配置

`fonts/` フォルダに `ipaexg.ttf` を配置してください。

IPAexフォントは以下からダウンロード可能です：
- https://moji.or.jp/ipafont/

```bash
# ダウンロード後
cp ~/Downloads/ipaexg.ttf fonts/
```

### 5. ローカル実行

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` を開きます。

## ☁️ Streamlit Cloud へのデプロイ

### 手順

1. GitHubにリポジトリをプッシュ
2. [Streamlit Cloud](https://streamlit.io/cloud) でアカウント作成・ログイン
3. 「New app」をクリック
4. リポジトリを選択
5. Main file path: `app.py` を指定
6. 「Deploy!」をクリック

### 注意事項

- `fonts/ipaexg.ttf` をリポジトリに含めてください
- Streamlit Cloudでは自動的に依存パッケージがインストールされます

## 📁 ファイル構成

```
aeon-segment-quarterly-analysis/
├── app.py                    # メインアプリケーション
├── requirements.txt          # 依存パッケージ
├── README.md                 # このファイル
├── LICENSE                   # ライセンス
├── .gitignore               # Git除外設定
├── .streamlit/
│   └── config.toml          # Streamlit設定
├── data/
│   └── segment_data.csv     # セグメント別業績データ
└── fonts/
    ├── README.md            # フォント設置説明
    └── ipaexg.ttf           # 日本語フォント（要配置）
```

## 📊 データ形式

`data/segment_data.csv` のカラム構成：

| カラム名 | 説明 | 例 |
|----------|------|-----|
| セグメント | セグメント名 | GMS事業 |
| 決算年度 | 四半期 | FY2025-3Q |
| 決算種別 | 種別（Q1/Q2/Q3/Q4） | Q3 |
| 営業収益 | 百万円 | 892,370 |
| 営業利益 | 百万円 | 4,088 |
| 営業利益率 | % | 0.5 |
| 営業収益構成比 | % | 35.0 |
| 営業利益構成比 | % | 6.9 |
| 設備投資 | 百万円 | 27,401 |

### データ期間

- FY2017-1Q 〜 FY2025-3Q（最新データ）
- 四半期ごとに9セグメント × 35四半期 = 315レコード

### データの更新方法

1. Excelで `segment_data.csv` を編集
2. UTF-8またはShift-JIS（cp932）で保存
3. アプリを再起動

## 🔧 カスタマイズ

### 色の変更

`app.py` の `segment_colors` を編集：

```python
segment_colors = {
    'GMS事業': '#1f77b4',
    'SM事業': '#ff7f0e',
    # ...
}
```

### 新しいセグメントの追加

1. `data/segment_data.csv` にデータを追加
2. `segment_colors` に色を追加
3. アプリを再起動

## 📝 ライセンス

MIT License

## ⚠️ 注意事項

- 本アプリケーションは分析・学習目的で作成されています
- データは公開情報を基に作成しています
- 投資判断の材料としてご使用の際は、必ず一次情報をご確認ください

## 🔗 関連プロジェクト

- [イオン 年度別セグメント業績分析ダッシュボード](https://github.com/YOUR_USERNAME/aeon-segment-analysis) - 年度単位での分析

## 🤝 貢献

Issue・Pull Request歓迎です！

## 📧 お問い合わせ

質問・要望がありましたら、Issueを作成してください。
