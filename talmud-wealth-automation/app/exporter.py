"""noteバンドル出力モジュール。storage から独立した出力レイヤー。"""

from __future__ import annotations

from pathlib import Path

from app.config import settings
from app.models import GeneratedContent
from app.storage import storage
from app.utils import save_markdown

NOTE_BUNDLE_TEMPLATE = """\
# note公開バンドル — {date}

---

## テーマ
{theme}

## 出典
{source}

---

# 無料note

## タイトル
{free_note_title}

## 本文

{free_note_body}

---

## 推奨導入文（任意で使用）
> タルムードに残された問いを、現代の仕事・商売・資産形成に翻訳するシリーズです。

## 推奨締め文（任意で使用）
> {cta_free}

---

# 有料note

## タイトル
{paid_note_title}

## 本文

{paid_note_body}

---

## 推奨締め文
> {cta_paid}

---

## タグ候補
{tags}

---

## 公開手順メモ

### 無料note
1. noteにログイン → 「投稿する」→「テキスト」を選択
2. タイトル・本文をコピペ（Markdown対応）
3. タグを設定 → 「全員に公開」→ 公開

### 有料note
1. 同様にテキスト投稿を作成
2. 「公開設定」→「有料」を選択
3. 価格を設定（推奨: 300〜500円）
4. 無料公開範囲を「無料公開部分まで」に設定 → 公開

---
*生成日時: {date}*
*ブランド: {brand_name}*
"""


def export_bundle(content: GeneratedContent, date_str: str) -> Path:
    """コンテンツからnote公開バンドルを生成して保存する。"""
    tag_list = settings.note.get("tag_candidates", [])
    tags_str = "  ".join(f"#{t}" for t in tag_list)
    cta = settings.cta
    brand_name = settings.brand.get("name", "タルムード資産論")

    bundle = NOTE_BUNDLE_TEMPLATE.format(
        date=date_str,
        theme=content.theme,
        source=content.source or "（出典未設定）",
        free_note_title=content.free_note_title,
        free_note_body=content.free_note_body,
        paid_note_title=content.paid_note_title,
        paid_note_body=content.paid_note_body,
        cta_free=cta.get("free_note", ""),
        cta_paid=cta.get("paid_note", ""),
        tags=tags_str,
        brand_name=brand_name,
    )
    path = storage.bundle_path(date_str)
    save_markdown(bundle, path)
    return path
