"""
コンテンツ生成スクリプト。

デフォルトは claude CLI 経由（Claude Pro ログイン認証）。APIキー不要。

Usage:
    python scripts/generate_content.py
    python scripts/generate_content.py --theme "約束を軽くする人に富は残らない"
    python scripts/generate_content.py --theme "..." --source "バヴァ・メツィア49a"
    python scripts/generate_content.py --claude-api   # APIキー版（課金あり）
    python scripts/generate_content.py --gpt          # GPT版（OpenAI APIキー必要）
"""

from __future__ import annotations

import sys
from pathlib import Path

# プロジェクトルートを sys.path に追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from app.config import settings
from app.models import ContentSource
from app.reviewer import ContentReviewer
from app.storage import storage
from app.theme_selector import theme_selector
from app.utils import setup_logger, today_str
from app.writer import get_writer

console = Console()
logger = setup_logger("generate", settings.log_dir())


@click.command()
@click.option("--theme", "-t", default=None, help="テーマを手動指定")
@click.option("--source", "-s", default="", help="出典を手動指定")
@click.option("--date", "-d", default=None, help="保存日付 (YYYY-MM-DD)、省略時は今日")
@click.option("--claude-api", "claude_api", is_flag=True, default=False, help="Anthropic APIキー版を使う（課金あり）")
@click.option("--gpt", is_flag=True, default=False, help="GPT版も生成する（比較用、OpenAI APIキー必要）")
@click.option("--skip-review", is_flag=True, default=False, help="ルールベースのチェックをスキップ")
def main(theme: str | None, source: str, date: str | None, claude_api: bool, gpt: bool, skip_review: bool) -> None:
    date_str = date or today_str()
    writer_type = "claude-api" if claude_api else "claude"
    auth_label = "Claude API (APIキー)" if claude_api else "Claude Code (Pro認証)"
    console.print(Panel(
        f"[bold]タルムード資産論 — コンテンツ生成[/bold]\n日付: {date_str}\n認証: {auth_label}",
        style="blue",
    ))

    # テーマ選定
    selected_theme = theme_selector.select(manual=theme)
    console.print(f"\n[green]テーマ:[/green] {selected_theme.title}")
    if source:
        selected_theme.source = source

    # Claude 生成
    console.print(f"\n[yellow]{auth_label} でコンテンツを生成中...[/yellow]")
    try:
        writer = get_writer(writer_type)
        claude_content = writer.generate(selected_theme.title, selected_theme.source)
    except Exception as e:
        console.print(f"[red]Claude 生成エラー: {e}[/red]")
        logger.error(f"Claude 生成エラー: {e}")
        raise SystemExit(1)

    # 保存
    saved_path = storage.save_content(claude_content, date_str)
    console.print(f"[green]Claude版保存:[/green] {saved_path}")

    # ルールベースチェック
    if not skip_review:
        rev = ContentReviewer()
        issues = rev.quick_check(claude_content)
        _print_issues(issues)

    # X投稿プレビュー
    _print_x_preview(claude_content)

    # GPT版生成（オプション）
    if gpt:
        console.print("\n[yellow]GPT でコンテンツを生成中...[/yellow]")
        try:
            gpt_writer = get_writer("gpt")
            gpt_content = gpt_writer.generate(selected_theme.title, selected_theme.source)
            gpt_path = storage.save_content(gpt_content, date_str)
            console.print(f"[green]GPT版保存:[/green] {gpt_path}")
        except Exception as e:
            console.print(f"[red]GPT 生成エラー: {e}[/red]")
            logger.warning(f"GPT 生成をスキップ: {e}")

    # テーマを使用済みに
    if not theme:  # 手動指定でない場合のみマーク
        theme_selector.mark_used(selected_theme)

    console.print("\n[bold green]生成完了[/bold green]")
    console.print(f"次: python scripts/review_content.py --date {date_str}")


def _print_issues(issues: dict[str, list[str]]) -> None:
    has_issue = any(v for v in issues.values())
    if not has_issue:
        console.print("[green]✓ ルールチェック: 問題なし[/green]")
        return

    table = Table(title="ルールチェック結果", show_header=True)
    table.add_column("セクション")
    table.add_column("問題点")
    for section, items in issues.items():
        for item in items:
            table.add_row(section, f"[red]{item}[/red]")
    console.print(table)


def _print_x_preview(content) -> None:
    status = "[green]✓[/green]" if content.x_valid else "[red]✗[/red]"
    console.print(
        Panel(
            f"{content.x_post}\n\n{status} {content.x_char_count}/280文字",
            title="X投稿プレビュー",
        )
    )


if __name__ == "__main__":
    main()
