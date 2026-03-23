# セットアップガイド — AI経済圏の創世

## 必要な環境

| 項目 | 要件 |
|------|------|
| OS | macOS / Linux |
| Python | 3.8 以上（標準ライブラリのみ使用） |
| Claude CLI | インストール済み（run_daily.sh を直接実行する場合のみ） |

### Claude CLI について
`scripts/run_daily.sh` はコマンドラインから `claude --print` を呼び出します。
インストール方法: https://docs.anthropic.com/claude-code

**Claude Code（GUI/IDE統合版）を使う場合は不要です。**
その場合は「Claude Code を開いて口頭で実行を指示する」方式で動作します。

---

## 初回セットアップ

### 1. リポジトリをクローン（または既存のリポジトリで使う場合はスキップ）
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. 初期化スクリプトを実行
```bash
./scripts/init.sh
```

このスクリプトは以下を行います：
- 必要なディレクトリの作成
- コンテキストファイルの初期化
- スクリプトへの実行権限付与

### 3. 確認
```bash
ls data/context/
# → bad_themes.md  focus_theme.md  good_themes.md  previous_log.json
```

---

## ディレクトリ構成

```
.
├── agents/                    # エージェント定義（役割・入出力仕様）
│   ├── observer_agent.md      # 市場仮説立案
│   ├── product_agent.md       # 小商品案生成
│   ├── post_agent.md          # X投稿案生成
│   ├── evaluator_agent.md     # 採点・採用判断
│   ├── recorder_agent.md      # 保存処理仕様
│   └── review_agent.md        # 週次レビュー生成
│
├── prompts/                   # Claude に渡すプロンプトテンプレート
│   ├── daily_system_prompt.md # 日次実験用
│   └── weekly_system_prompt.md# 週次レビュー用
│
├── scripts/                   # 実行スクリプト
│   ├── run_daily.sh           # 日次実験実行（メインコマンド）
│   ├── run_weekly.sh          # 週次レビュー実行
│   ├── init.sh                # 初回初期化
│   ├── export_notion.py       # JSON→Notion用MD変換
│   └── export_product.py      # JSON→商品案ストックMD変換
│
├── data/
│   ├── daily_logs/            # 日次JSON（YYYY-MM-DD.json）
│   ├── notion_exports/        # Notion用MD（YYYY-MM-DD.md）
│   ├── product_ideas/         # 商品案ストック（YYYY-MM-DD.md）
│   ├── weekly_reviews/        # 週次レビュー（YYYY-Wxx.md）
│   └── context/               # 実験コンテキスト（手動管理）
│       ├── previous_log.json  # 前日のログ（自動更新）
│       ├── good_themes.md     # 反応が良かったテーマ（手動更新）
│       ├── bad_themes.md      # 反応が悪かったテーマ（手動更新）
│       └── focus_theme.md     # 今日の重点テーマ（手動設定）
│
└── docs/
    ├── setup.md               # このファイル
    └── operation.md           # 毎日の運用手順
```

---

## コンテキストファイルの管理

### `data/context/previous_log.json`
- 自動更新（`run_daily.sh` が毎回更新する）
- 手動で触る必要はない

### `data/context/good_themes.md`
- 週次レビュー後に手動で追記する
- 書き方: `- テーマ名：説明（実験日）`

### `data/context/bad_themes.md`
- 週次レビュー後に手動で追記する
- 書き方: `- テーマ名：なぜ避けるか（実験日）`

### `data/context/focus_theme.md`
- 毎朝（または週初めに）手動で設定する
- 空でも動作する（observer_agent が自律的に仮説を立てる）
- 特定テーマを連続検証したい場合に活用する
