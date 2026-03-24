# タルムード資産論 コンテンツ管理システム

「富は、思考の質から生まれる。」

タルムードやラビ文学の逸話・問い・判断を、現代の仕事・商売・資産形成に翻訳し、
日本の読者に向けて発信する知的ブランドのコンテンツ管理システムです。

## 機能

- コンテンツ（X投稿 / 無料note / 有料note）の作成・管理
- テーマカテゴリによる分類
- 下書き・公開のワークフロー管理
- 管理画面（`/admin`）

## セットアップ

```bash
bundle install
rails db:create db:migrate db:seed
rails server
```

## URL構成

| パス | 説明 |
|---|---|
| `/` | コンテンツ一覧（公開済み） |
| `/contents/:id` | コンテンツ詳細 |
| `/admin/contents` | 管理画面一覧 |
| `/admin/contents/new` | 新規作成 |
| `/admin/contents/:id/edit` | 編集 |

## コンテンツモデル

各コンテンツは以下のフィールドを持ちます：

- `title` — テーマタイトル
- `source` — 原典（例：バビロニア・タルムード マコット24a）
- `theme_category` — 信用 / 契約 / 判断 / 欲望 / 自制 / 長期視点 / 問いを立てる力
- `x_post` — X投稿文（280文字以内）
- `free_note_title` — 無料noteタイトル
- `free_note_body` — 無料note本文（Markdown）
- `paid_note_title` — 有料noteタイトル
- `paid_note_body` — 有料note本文（Markdown）
- `status` — `draft`（下書き）/ `published`（公開済み）
- `published_at` — 公開日時
