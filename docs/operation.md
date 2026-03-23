# 運用ガイド — AI経済圏の創世

## 毎日の運用フロー（所要時間：5〜15分）

### 朝のルーティン

```
1. （任意）focus_theme.md を更新する                      ← 2分
2. 日次実験を実行する                                      ← 1分（実行するだけ）
3. 採用投稿の文字数を確認してXに投稿する                   ← 3〜5分
4. data/note_drafts/YYYY-MM-DD.md を確認・軽く編集する     ← 3〜5分
5. noteに投稿する（任意・手動）                            ← 2〜3分
6. 商品案を見て、実際に作れるか判断する                    ← 2〜3分
```

---

## 実行コマンド

### 日次実験（毎日）
```bash
# Claude CLI 経由
./scripts/run_daily.sh

# 日付を指定して実行
./scripts/run_daily.sh 2026-03-25

# Claude Code 経由（CLI不要）
# Claude Code を開いて「今日の日次実験を実行して」と伝える
```

### 週次レビュー（週1回）
```bash
# 直近7日間を自動集計
./scripts/run_weekly.sh

# 期間指定
./scripts/run_weekly.sh 2026-03-16 2026-03-22
```

### 個別変換（必要に応じて）
```bash
# JSON→Notion用MD
python3 scripts/export_notion.py data/daily_logs/2026-03-23.json data/notion_exports/2026-03-23.md

# JSON→商品案ストックMD
python3 scripts/export_product.py data/daily_logs/2026-03-23.json data/product_ideas/2026-03-23.md

# JSON→note記事ドラフトMD
python3 scripts/save_note.py data/daily_logs/2026-03-23.json data/note_drafts/2026-03-23.md
```

---

## 実験完了後の確認チェックリスト

実行後に毎回確認すること：

- [ ] 採用投稿のX文字数を確認した（X入力画面で280字以内か）
- [ ] 商品案の概要を読んで、作成可能か判断した
- [ ] 明日の改善仮説をメモした（focus_theme.md に入れてもよい）
- [ ] JSONファイルが正しく保存されていることを確認した

---

## 週次レビュー後の作業

```
1. data/weekly_reviews/YYYY-Wxx.md を読む
2. good_themes.md を更新する
3. bad_themes.md を更新する
4. focus_theme.md に来週の重点テーマを設定する
5. 有望商品案があれば、実際の商品化作業を始める
```

---

## データの流れ

```
context/focus_theme.md
context/good_themes.md         ──┐
context/bad_themes.md            │
context/previous_log.json        │
context/membership_strategy.md   │
                                 ↓
                   prompts/daily_system_prompt.md
                                 ↓
                          Claude が実験実行
                                 ↓
                 data/daily_logs/YYYY-MM-DD.json
            ↙          ↓          ↓          ↘
export_notion.py  export_product.py  save_note.py
      ↓                ↓                ↓
notion_exports/   product_ideas/   note_drafts/
YYYY-MM-DD.md    YYYY-MM-DD.md    YYYY-MM-DD.md
                                 ↓
                 context/previous_log.json（上書き更新）
```

---

## Notion への貼り付け方

1. `data/notion_exports/YYYY-MM-DD.md` を開く
2. 内容をコピー
3. Notion のページに `/markdown` で貼り付け、またはそのままペースト

---

## 商品案の管理

`data/product_ideas/` に毎日蓄積される。

月1回程度、以下の観点で棚卸しすることを推奨：
- 商品化優先度「高」のものを実際に作り始める
- 類似した商品案をまとめてシリーズ化を検討する
- 反応が良かったX投稿と紐づけて価値検証する

---

## トラブルシューティング

### JSONが正しく生成されない
- `data/daily_logs/YYYY-MM-DD_raw.txt` を確認する
- Claude の出力がJSON形式でない場合に発生する
- raw.txt を手動でJSONに整形して `.json` として保存する

### claude コマンドが見つからない
- Claude CLI をインストールする: https://docs.anthropic.com/claude-code
- または Claude Code（GUI版）を使って口頭で実行を指示する

### 前日ログが参照されていない
- `data/context/previous_log.json` が正しく更新されているか確認する
- `cat data/context/previous_log.json | python3 -m json.tool` で検証する

---

## 朝5時の自動実行（cron設定）

### cron に登録する方法

```bash
# crontab を開く
crontab -e

# 以下の1行を追記する（/home/user/rails を実際のパスに変更すること）
0 5 * * * cd /home/user/rails && ./scripts/run_daily.sh >> /home/user/rails/data/cron_log.txt 2>&1
```

### 解説
- `0 5 * * *` ：毎朝5:00に実行（日本時間にするにはサーバーのタイムゾーンを確認すること）
- 出力は `data/cron_log.txt` に蓄積される
- `run_daily.sh` の中で `claude` CLI が呼ばれる（要インストール）

### タイムゾーンの確認

```bash
# 現在のタイムゾーン確認
timedatectl

# 日本時間（JST）に設定する場合
sudo timedatectl set-timezone Asia/Tokyo
```

### Claude Code（GUI版）での代替方法
- Claude Code を朝に開いて「今日の日次実験を実行して」と伝えるだけでも動く
- CLIが不要なため、最も手軽な方法

---

## note記事の管理

`data/note_drafts/` に毎日のドラフトが蓄積される。

### 投稿前のチェックリスト
- [ ] 1000字前後か確認する（大きくずれている場合は補足・要約する）
- [ ] 誇大表現・煽り文句がないか確認する
- [ ] 「今日の気づき」「再現のヒント」「次回への興味」が含まれているか確認する
- [ ] メンバーシップへの自然な誘導文があるか確認する

### メンバーシップ移行の目安
`data/context/membership_strategy.md` に方針を記載している。
30日分以上蓄積され、スキ数が安定してきたタイミングで有料化を検討する。

---

## 将来の拡張ポイント

以下は現時点では実装していないが、後から追加できる拡張先：

| 拡張 | 概要 | 必要なもの |
|------|------|-----------|
| Notion API連携 | 日次ログを自動でNotionに保存 | Notion APIキー・Python SDK |
| X自動投稿 | 採用投稿をX APIで自動投稿 | X API v2キー・OAuth設定 |
| Slack通知 | 実験完了をSlackに通知 | Webhook URL |
| スコア集計ダッシュボード | 日次スコアをグラフ化 | matplotlib等 |
| 複数仮説の並列実験 | 1日で複数仮説を検証 | スクリプト改修 |
| AI採点の精度向上 | 実際のX反応データを採点にフィードバック | X APIアクセス |

拡張する際は `agents/` の対応エージェント定義ファイルを先に更新し、
`scripts/` にロジックを追加することを推奨する。
