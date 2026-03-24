"""
コンテンツ整形スクリプト。

Usage:
    python scripts/format_content.py
    python scripts/format_content.py --date 2026-03-25
    python scripts/format_content.py --date 2026-03-25 --quick
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from rich.console import Console
from rich.panel import Panel

from app.config import settings
from app.formatter import ContentFormatter
from app.models import ContentSource
from app.storage import storage
from app.utils import setup_logger, today_str

console = Console()
logger = setup_logger("format", settings.log_dir())


@click.command()
@click.option("--date", "-d", default=None, help="整形対象日付 (YYYY-MM-DD)")
@click.option("--quick", is_flag=True, default=False, help="APIを使わず軽量整形のみ")
def main(date: str | None, quick: bool) -> None:
    date_str = date or today_str()
    console.print(Panel(f"[bold]タルムード資産論 — 整形[/bold]\n日付: {date_str}", style="blue"))

    # 採用版を決定（レビューがあれば従う）
    review = storage.load_review(date_str)
    if review and review.recommendation.value == "gpt_adopt":
        source = "gpt"
        console.print("[cyan]レビュー: GPT版を採用します[/cyan]")
    else:
        source = "claude"
        console.print("[cyan]レビュー: Claude版を採用します[/cyan]")

    content = storage.load_content(date_str, source)
    if not content:
        console.print(f"[red]{source}版が見つかりません: {date_str}[/red]")
        raise SystemExit(1)

    fmt = ContentFormatter()

    if quick:
        # X投稿だけ軽量整形
        console.print("[yellow]--quick モード: X投稿のみ整形します[/yellow]")
        text, count, valid = fmt.format_x_only(content.x_post)
        content.x_post = text
        formatted = content
    else:
        console.print("[yellow]Claude で整形中...[/yellow]")
        try:
            formatted = fmt.format(content)
        except Exception as e:
            console.print(f"[red]整形エラー: {e} — 軽量整形にフォールバックします[/red]")
            logger.warning(f"API整形失敗: {e} — 軽量整形を使用")
            text, _, _ = fmt.format_x_only(content.x_post)
            content.x_post = text
            formatted = content

    # 各ファイル保存
    storage.save_final(formatted, date_str)
    x_path = storage.save_x_post(formatted.x_post, date_str)
    fn_path = storage.save_free_note(formatted.free_note_title, formatted.free_note_body, date_str)
    pn_path = storage.save_paid_note(formatted.paid_note_title, formatted.paid_note_body, date_str)

    console.print(f"\n[green]保存完了:[/green]")
    console.print(f"  X投稿     : {x_path}")
    console.print(f"  無料note  : {fn_path}")
    console.print(f"  有料note  : {pn_path}")

    # X投稿プレビュー
    status = "[green]✓[/green]" if formatted.x_valid else "[red]✗ 280文字超過[/red]"
    console.print(
        Panel(
            f"{formatted.x_post}\n\n{status} {formatted.x_char_count}/280文字",
            title="X投稿（整形後）",
        )
    )

    console.print(f"\n次: python scripts/publish_x.py --date {date_str} --dry-run")
    console.print(f"    python scripts/export_note_bundle.py --date {date_str}")


if __name__ == "__main__":
    main()
