"""
コンテンツレビュースクリプト。

Usage:
    python scripts/review_content.py
    python scripts/review_content.py --date 2026-03-25
    python scripts/review_content.py --date 2026-03-25 --quick
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from app.config import settings
from app.reviewer import ContentReviewer
from app.storage import storage
from app.utils import setup_logger, today_str

console = Console()
logger = setup_logger("review", settings.log_dir())


@click.command()
@click.option("--date", "-d", default=None, help="レビュー対象日付 (YYYY-MM-DD)")
@click.option("--quick", is_flag=True, default=False, help="APIを使わずルールベースのみ")
def main(date: str | None, quick: bool) -> None:
    date_str = date or today_str()
    console.print(Panel(f"[bold]タルムード資産論 — レビュー[/bold]\n日付: {date_str}", style="blue"))

    # Claude版を読み込む
    claude_content = storage.load_content(date_str, "claude")
    if not claude_content:
        console.print(f"[red]Claude版が見つかりません: {date_str}[/red]")
        console.print("先に generate_content.py を実行してください")
        raise SystemExit(1)

    rev = ContentReviewer()

    # ルールベースチェック（常に実行）
    issues = rev.quick_check(claude_content)
    _print_issues(issues)

    if quick:
        console.print("[yellow]--quick モード: APIレビューをスキップします[/yellow]")
        raise SystemExit(0)

    # GPT版があれば比較
    gpt_content = storage.load_content(date_str, "gpt")
    if gpt_content:
        console.print("[cyan]GPT版が見つかりました。比較レビューを実行します。[/cyan]")
    else:
        console.print("[dim]GPT版なし。Claude版のみレビューします。[/dim]")

    # APIレビュー
    console.print("\n[yellow]Claude でレビュー中...[/yellow]")
    try:
        review = rev.review(claude_content, compare_with=gpt_content)
    except Exception as e:
        console.print(f"[red]レビューエラー: {e}[/red]")
        logger.error(f"レビューエラー: {e}")
        raise SystemExit(1)

    # 保存
    saved_path = storage.save_review(review, date_str)
    console.print(f"[green]レビュー保存:[/green] {saved_path}")

    # 結果表示
    _print_review(review)
    console.print(f"\n次: python scripts/format_content.py --date {date_str}")


def _print_issues(issues: dict[str, list[str]]) -> None:
    has_issue = any(v for v in issues.values())
    if not has_issue:
        console.print("[green]✓ ルールチェック: 問題なし[/green]")
        return
    for section, items in issues.items():
        for item in items:
            console.print(f"  [red]✗ {section}:[/red] {item}")


def _print_review(review) -> None:
    # スコアテーブル
    table = Table(title=f"レビュースコア（総合: {review.overall_score:.1f}）")
    table.add_column("項目")
    table.add_column("★", justify="center")
    for criterion, score in review.scores.items():
        stars = "★" * score + "☆" * (5 - score)
        table.add_row(criterion, stars)
    console.print(table)

    # 採用判断
    rec_color = {"claude_adopt": "green", "gpt_adopt": "yellow", "hybrid": "cyan"}
    color = rec_color.get(review.recommendation.value, "white")
    console.print(f"\n[bold {color}]採用判断: {review.recommendation.value}[/bold {color}]")
    console.print(f"[dim]{review.summary}[/dim]")

    # 改善提案
    if review.improvements:
        console.print("\n[bold]改善提案:[/bold]")
        for imp in review.improvements:
            console.print(f"  • [yellow]{imp.get('target', '')}[/yellow]")
            if imp.get("after"):
                console.print(f"    → {imp['after']}")


if __name__ == "__main__":
    main()
