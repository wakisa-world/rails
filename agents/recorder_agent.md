# recorder_agent — 保存処理エージェント

## 役割
全エージェントの出力を統合し、以下の3ファイルを生成・保存する。
AIによる生成ではなく、**データ変換と保存**が主務。
実際の保存処理は `scripts/run_daily.sh` が担う。

## 入力
全エージェントの出力を統合した最終JSON（日次実験の全フィールド）

## 出力ファイル一覧

### 1. 日次JSON
**保存先**: `data/daily_logs/YYYY-MM-DD.json`

完全なスキーマ：
```json
{
  "date": "YYYY-MM-DD",
  "market_hypothesis": {
    "theme": "",
    "reason": ""
  },
  "product_idea": {
    "type": "",
    "title": "",
    "target": "",
    "transformation": "",
    "outline": ["", "", ""],
    "price_hint": "",
    "score": 0,
    "score_reason": ""
  },
  "x_posts": [
    {
      "type": "思想寄り",
      "hook": "",
      "body": "",
      "score": 0,
      "score_reason": ""
    },
    {
      "type": "実験記録寄り",
      "hook": "",
      "body": "",
      "score": 0,
      "score_reason": ""
    },
    {
      "type": "学び寄り",
      "hook": "",
      "body": "",
      "score": 0,
      "score_reason": ""
    }
  ],
  "selected_post_index": 0,
  "selection_reason": "",
  "tomorrow_hypothesis": "",
  "operation_note": {
    "human_check_points": ["", ""],
    "reuse_idea": ""
  }
}
```

### 2. Notion貼り付け用Markdown
**保存先**: `data/notion_exports/YYYY-MM-DD.md`
**生成**: `scripts/export_notion.py` が日次JSONから変換

### 3. 商品案ストックMarkdown
**保存先**: `data/product_ideas/YYYY-MM-DD.md`
**生成**: `scripts/export_product.py` が日次JSONから変換

## コンテキスト更新
実験完了後、`data/context/previous_log.json` を今日のJSONで上書きする。

## エラー処理方針
- JSONが不正な場合はそのまま保存し、ログにエラーを記録する
- 既存ファイルは上書きせず、`-v2` サフィックスを付ける
- コンテキストファイルが存在しない場合は空として扱う（エラーにしない）

## 引き継ぎ
recorder_agent の処理完了後、人間に要約を表示して確認を促す。
