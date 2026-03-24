"""
note用バンドル出力スクリプト。
無料note・有料note をnoteに貼り付けやすい形でまとめる。

Usage:
    python scripts/export_note_bundle.py
    python scripts/export_note_bundle.py --date 2026-03-25
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from rich.console import Console
from rich.panel import Panel

from app.config import settings
from app.storage import storage
from app.utils import save_markdown, setup_logger, today_str

console = Console()
logger = setup_logger("export", settings.log_dir())


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

## 推奨導入文（任意で使用）
> タルムードの逸話から、現代の現場で使える思考を取り出すシリーズです。

## 推奨締め文
> {cta_paid}

---

## タグ候補
{tags}

---

## 公開手順メモ

### 無料note
1. noteにログイン
2. 「投稿する」→「テキスト」を選択
3. タイトルをコピペ
4. 本文をコピペ（Markdown対応）
5. タグを設定
6. 「公開設定」→「全員に公開」
7. 公開

### 有料note
1. 上記と同様にテキスト投稿を作成
2. 「公開設定」→「有料」を選択
3. 価格を設定（推奨: 300〜500円）
4. 無料公開範囲を「無料note本文まで」に設定
5. 公開

---
*生成日時: {date}*
*ブランド: {brand_name}*
"""


def _export_bundle(content, date_str: str) -> Path:
    """run_daily.py から直接呼び出せるヘルパー。"""
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
    bundle_path = storage.bundle_path(date_str)
    save_markdown(bundle, bundle_path)
    return bundle_path


@click.command()
@click.option("--date", "-d", default=None, help="対象日付 (YYYY-MM-DD)")
def main(date: str | None) -> None:
    date_str = date or today_str()
    console.print(Panel(f"[bold]タルムード資産論 — noteバンドル出力[/bold]\n日付: {date_str}", style="blue"))

    # 整形済み最終版を読み込む（フォールバック: Claude版）
    content = storage.load_final(date_str) or storage.load_content(date_str, "claude")
    if not content:
        console.print(f"[red]コンテンツが見つかりません: {date_str}[/red]")
        raise SystemExit(1)

    bundle_path = _export_bundle(content, date_str)
    console.print(f"[green]バンドル保存:[/green] {bundle_path}")
    console.print("\n[dim]このファイルをnoteに貼り付けて公開してください。[/dim]")


if __name__ == "__main__":
    main()
