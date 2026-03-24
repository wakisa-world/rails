"""
テーマ管理スクリプト。テーマの追加・一覧・ステータス変更を行う。

Usage:
    python scripts/manage_themes.py list
    python scripts/manage_themes.py add --title "テーマ名" --source "出典" --category "信用"
    python scripts/manage_themes.py reset --title "テーマ名"  # 使用済み→未使用に戻す
    python scripts/manage_themes.py stats
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from rich.console import Console
from rich.table import Table

from app.config import settings
from app.models import Theme, ThemeStatus
from app.theme_selector import theme_selector
from app.utils import today_str

console = Console()

CATEGORIES = ["信用", "契約", "判断", "欲望", "自制", "長期視点", "問いを立てる力"]


@click.group()
def cli() -> None:
    """テーマ管理ツール"""


@cli.command()
@click.option("--status", "-s", default=None, type=click.Choice(["unused", "used", "pending"]))
def list(status: str | None) -> None:
    """テーマ一覧を表示する。"""
    themes = theme_selector.all_themes()
    if status:
        themes = [t for t in themes if t.status.value == status]

    if not themes:
        console.print("[yellow]テーマがありません[/yellow]")
        return

    table = Table(title=f"テーマ一覧（{len(themes)}件）", show_lines=True)
    table.add_column("タイトル", max_width=40)
    table.add_column("カテゴリ", width=12)
    table.add_column("ステータス", width=10)
    table.add_column("使用日", width=12)
    table.add_column("出典", max_width=30)

    status_colors = {
        ThemeStatus.UNUSED: "green",
        ThemeStatus.USED: "dim",
        ThemeStatus.PENDING: "yellow",
    }
    for t in themes:
        color = status_colors.get(t.status, "white")
        table.add_row(
            t.title,
            t.category or "—",
            f"[{color}]{t.status.value}[/{color}]",
            t.used_date or "—",
            t.source or "—",
        )
    console.print(table)


@cli.command()
@click.option("--title", "-t", required=True, help="テーマタイトル")
@click.option("--source", "-s", default="", help="出典")
@click.option("--category", "-c", default="", type=click.Choice(CATEGORIES + [""]))
@click.option("--description", "-d", default="", help="テーマ概要")
@click.option("--tags", default="", help="タグ（カンマ区切り）")
def add(title: str, source: str, category: str, description: str, tags: str) -> None:
    """新しいテーマを追加する。"""
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    theme = Theme(
        title=title,
        source=source,
        category=category,
        description=description,
        tags=tag_list,
        status=ThemeStatus.UNUSED,
    )
    path = theme_selector.add_theme(theme)
    console.print(f"[green]追加完了:[/green] {path}")


@cli.command()
@click.argument("title")
def reset(title: str) -> None:
    """使用済みテーマを未使用に戻す。"""
    themes = theme_selector.all_themes()
    matched = [t for t in themes if t.title == title]
    if not matched:
        console.print(f"[red]テーマが見つかりません: {title}[/red]")
        raise SystemExit(1)
    theme = matched[0]
    theme.status = ThemeStatus.UNUSED
    theme.used_date = ""
    path = theme_selector.theme_dir / f"{theme_selector._theme_filename(theme.title)}.json"
    if path.exists():
        theme.save(path)
        console.print(f"[green]リセット完了: {title}[/green]")
    else:
        console.print(f"[yellow]ファイルが見つかりません。手動で更新してください。[/yellow]")


@cli.command()
def stats() -> None:
    """テーマの統計情報を表示する。"""
    summary = theme_selector.list_summary()
    console.print("\n[bold]テーマ統計[/bold]")
    console.print(f"  合計    : {summary['total']}")
    console.print(f"  [green]未使用[/green]  : {summary['unused']}")
    console.print(f"  [dim]使用済み[/dim]: {summary['used']}")
    console.print(f"  [yellow]保留中[/yellow]  : {summary['pending']}")

    # カテゴリ別
    all_themes = theme_selector.all_themes()
    cat_count: dict[str, int] = {}
    for t in all_themes:
        cat = t.category or "未分類"
        cat_count[cat] = cat_count.get(cat, 0) + 1

    if cat_count:
        console.print("\n[bold]カテゴリ別[/bold]")
        for cat, cnt in sorted(cat_count.items(), key=lambda x: -x[1]):
            console.print(f"  {cat}: {cnt}")


if __name__ == "__main__":
    cli()
