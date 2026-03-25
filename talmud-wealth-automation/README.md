# talmud-wealth-automation

**タルムード資産論** ブランドのコンテンツ自動生成・整形・X投稿補助システム。

> 富は、思考の質から生まれる。

毎日、タルムードやラビ文学の逸話を現代の仕事・商売・資産形成に翻訳した
X投稿・無料note・有料noteを生成・整形・保存する。

---

## ディレクトリ構成

```
talmud-wealth-automation/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   ├── settings.yaml       # ブランド設定・生成設定
│   └── prompts.yaml        # ブランド方針・品質基準
├── data/
│   ├── themes/             # テーマ候補（JSON）
│   ├── sources/            # 原典メモ
│   └── queue/              # 生成待ちキュー
├── prompts/
│   ├── project_prompt.md   # ブランド全体方針
│   ├── writer_prompt.md    # ライター指示
│   ├── reviewer_prompt.md  # レビュアー指示
│   └── formatter_prompt.md # 整形担当指示
├── outputs/
│   ├── x/                  # X投稿テキスト
│   ├── free_note/          # 無料note Markdown
│   ├── paid_note/          # 有料note Markdown
│   └── final/              # 採用確定版 + noteバンドル
├── reviews/                # レビュー結果JSON
├── logs/                   # 日付別ログ
├── scripts/
│   ├── run_daily.py        # 日次一括実行
│   ├── generate_content.py # コンテンツ生成
│   ├── review_content.py   # レビュー
│   ├── format_content.py   # 整形
│   ├── publish_x.py        # X投稿
│   └── export_note_bundle.py # noteバンドル出力
└── app/
    ├── config.py           # 設定管理
    ├── models.py           # データモデル
    ├── theme_selector.py   # テーマ選定
    ├── writer.py           # 生成（Claude/GPT）
    ├── reviewer.py         # レビュー
    ├── formatter.py        # 整形
    ├── publisher.py        # X投稿
    ├── storage.py          # ファイル保存
    └── utils.py            # ログ・ユーティリティ
```

---

## セットアップ

> **APIキー不要。Claude Pro ログイン認証で動作します。**

### 前提: Claude Code のインストール

```bash
npm install -g @anthropic-ai/claude-code
```

インストール済み確認:

```bash
claude --version
```

### 1. Claude Pro でログイン（初回のみ）

```bash
claude login
```

ブラウザが開くので Claude Pro アカウントでログイン。
以降はトークンが `~/.claude.json` に保存されるため、再ログイン不要。

### 2. 依存インストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数を設定

```bash
cp .env.example .env
# デフォルト設定のまま使える（APIキー不要）
```

APIキーは**不要**。必要に応じてコメントアウトされた項目を設定する:
- `ANTHROPIC_API_KEY` — `--claude-api` フラグ使用時のみ（課金あり）
- `OPENAI_API_KEY` — `--gpt` フラグ使用時のみ
- `X_API_KEY` 等 — X自動投稿を使う場合のみ

### 4. テーマを追加

`data/themes/` にJSONファイルを置く。

```json
{
  "title": "テーマタイトル",
  "source": "バビロニア・タルムード ○○篇 ○a",
  "category": "信用",
  "description": "テーマの概要",
  "status": "unused",
  "used_date": "",
  "tags": ["タグ1", "タグ2"]
}
```

サンプルは `data/themes/sample_01.json` 〜 `sample_03.json` を参照。

---

## 動作確認

### モック（claude login 不要）

```bash
python scripts/test_mock.py
```

APIキー・ログインなしでフルフロー（保存・チェック・整形・バンドル出力）を確認できる。

### Claude Pro 認証で実際に生成

```bash
# claude login 完了後
python scripts/generate_content.py
```

---

## 使い方

### セットアップ確認

```bash
python scripts/check_setup.py
```

### テーマ管理

```bash
# 一覧
python scripts/manage_themes.py list
python scripts/manage_themes.py list --status unused

# 追加
python scripts/manage_themes.py add --title "テーマ名" --source "出典" --category "信用"

# 統計
python scripts/manage_themes.py stats

# 使用済み→未使用に戻す
python scripts/manage_themes.py reset "テーマ名"
```

### 日次一括実行（推奨）

```bash
python scripts/run_daily.py
```

オプション:
```bash
python scripts/run_daily.py --theme "手動でテーマを指定"
python scripts/run_daily.py --skip-review   # APIレビューをスキップ
python scripts/run_daily.py --gpt           # GPT版も生成して比較
```

### ステップごとに実行

```bash
# 1. 生成（Claude Pro 認証、APIキー不要）
python scripts/generate_content.py
python scripts/generate_content.py --theme "約束を軽くする人に富は残らない"

# APIキー版を使う場合（.env に ANTHROPIC_API_KEY が必要）
python scripts/generate_content.py --claude-api

# 2. レビュー
python scripts/review_content.py --date 2026-03-25
python scripts/review_content.py --date 2026-03-25 --quick  # ルールベースのみ

# 3. 整形
python scripts/format_content.py --date 2026-03-25
python scripts/format_content.py --date 2026-03-25 --quick  # 軽量整形

# 4. X投稿（dry-run で確認してから）
python scripts/publish_x.py --date 2026-03-25 --dry-run
python scripts/publish_x.py --date 2026-03-25

# 5. noteバンドル出力
python scripts/export_note_bundle.py --date 2026-03-25
```

### cron 設定（毎朝5時）

```bash
0 5 * * * cd /path/to/talmud-wealth-automation && python scripts/run_daily.py >> logs/cron.log 2>&1
```

---

## 出力ファイル

| ファイル | 内容 |
|---|---|
| `outputs/x/YYYYMMDD.txt` | X投稿テキスト |
| `outputs/free_note/YYYYMMDD.md` | 無料note Markdown |
| `outputs/paid_note/YYYYMMDD.md` | 有料note Markdown |
| `outputs/final/YYYYMMDD.json` | 採用確定版（JSON） |
| `outputs/final/YYYYMMDD_bundle.md` | note公開バンドル |
| `reviews/YYYYMMDD_review.json` | レビュー結果 |
| `logs/YYYY-MM-DD.log` | 実行ログ |

---

## ブランド方針

詳細は `prompts/project_prompt.md` と `config/prompts.yaml` を参照。

### 禁止事項
- ユダヤ人全体の一般化
- 宗教・民族の神秘化
- 陰謀論的表現
- 出典不明の名言の断定利用
- 「金持ち確定」等の誇張
- 露骨な情報商材表現

---

### 過去出力の確認

```bash
# 出力一覧
python scripts/view_output.py --list

# 今日の出力全体
python scripts/view_output.py

# 特定日・特定セクション
python scripts/view_output.py --date 2026-03-25 --section x
python scripts/view_output.py --date 2026-03-25 --section review
```

---

## TODO（次の実装候補）

- [ ] GPT比較の自動実行フロー完成
- [ ] テーマ候補の自動蓄積スクリプト
- [ ] note公開APIの統合（将来）
- [ ] Slack/LINE通知（生成完了時）
- [ ] Webダッシュボード（生成履歴・品質スコア可視化）
- [ ] テーマカテゴリ別のバランス管理
- [ ] 過去コンテンツの検索・再利用

---

## ライセンス

Private — タルムード資産論ブランド専用
