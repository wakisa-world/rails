"""
過去の出力を確認するスクリプト。

Usage:
    python scripts/view_output.py                    # 今日の出力
    python scripts/view_output.py --date 2026-03-25
    python scripts/view_output.py --date 2026-03-25 --section x
    python scripts/view_output.py --list             # 過去の出力一覧
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from app.config import settings
from app.storage import storage
from app.utils import today_str

console = Console()


@click.command()
@click.option("--date", "-d", default=None, help="確認する日付 (YYYY-MM-DD)")
@click.option("--section", "-s", default="all",
              type=click.Choice(["all", "x", "free", "paid", "review"]),
              help="表示するセクション")
@click.option("--list", "list_mode", is_flag=True, default=False, help="過去の出力一覧を表示")
def main(date: str | None, section: str, list_mode: bool) -> None:
    if list_mode:
        _show_list()
        return

    date_str = date or today_str()
    console.print(Panel(f"[bold]タルムード資産論 — 出力確認[/bold]\n日付: {date_str}", style="blue"))

    content = storage.load_final(date_str) or storage.load_content(date_str, "claude")
    if not content:
        console.print(f"[red]出力が見つかりません: {date_str}[/red]")
        raise SystemExit(1)

    console.print(f"[dim]テーマ: {content.theme}[/dim]")
    console.print(f"[dim]出典: {content.source}[/dim]\n")

    if section in ("all", "x"):
        valid = "[green]✓[/green]" if content.x_valid else "[red]✗[/red]"
        console.print(Panel(
            f"{content.x_post}\n\n{valid} {content.x_char_count}/280文字",
            title="X投稿",
        ))

    if section in ("all", "free"):
        console.print(Panel(
            Markdown(f"# {content.free_note_title}\n\n{content.free_note_body}"),
            title="無料note",
        ))

    if section in ("all", "paid"):
        console.print(Panel(
            Markdown(f"# {content.paid_note_title}\n\n{content.paid_note_body}"),
            title="有料note",
        ))

    if section in ("all", "review"):
        review = storage.load_review(date_str)
        if review:
            table = Table(title=f"レビュースコア（総合: {review.overall_score:.1f}）")
            table.add_column("項目")
            table.add_column("★", justify="center")
            for criterion, score in review.scores.items():
                stars = "★" * score + "☆" * (5 - score)
                table.add_row(criterion, stars)
            console.print(table)
            rec_colors = {"claude_adopt": "green", "gpt_adopt": "yellow", "hybrid": "cyan"}
            color = rec_colors.get(review.recommendation.value, "white")
            console.print(f"採用判断: [{color}]{review.recommendation.value}[/{color}]")
        else:
            console.print("[dim]レビューなし[/dim]")


def _show_list() -> None:
    final_dir = settings.output_dir("final")
    files = sorted(final_dir.glob("????????.json"), reverse=True)

    if not files:
        console.print("[yellow]出力履歴がありません[/yellow]")
        return

    table = Table(title="出力履歴", show_lines=False)
    table.add_column("日付")
    table.add_column("テーマ", max_width=40)

    table.add_column("X文字数", width=8)
    table.add_column("レビュー")

    import json
    for path in files[:20]:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        date_raw = path.stem
        date_fmt = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:]}"
        x_count = len(data.get("x_post", ""))
        x_ok = "[green]✓[/green]" if x_count <= 280 else "[red]✗[/red]"

        review = storage.load_review(date_fmt)
        rev_str = f"{review.overall_score:.1f}" if review else "—"

        table.add_row(date_fmt, data.get("theme", "—")[:40], f"{x_ok} {x_count}", rev_str)

    console.print(table)


if __name__ == "__main__":
    main()
