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
from app.exporter import export_bundle
from app.storage import storage
from app.utils import setup_logger, today_str

console = Console()
logger = setup_logger("export", settings.log_dir())


@click.command()
@click.option("--date", "-d", default=None, help="対象日付 (YYYY-MM-DD)")
def main(date: str | None) -> None:
    date_str = date or today_str()
    console.print(Panel(f"[bold]タルムード資産論 — noteバンドル出力[/bold]\n日付: {date_str}", style="blue"))

    # 整形済み最終版を読み込む（フォールバック: Claude版）
    content = storage.load_final(date_str) or storage.load_content(date_str, "claude")
    if not content:
        console.print(f"[red]コンテンツが見つかりません: {date_str}[/red]")
        console.print("先に generate_content.py と format_content.py を実行してください")
        raise SystemExit(1)

    bundle_path = export_bundle(content, date_str)
    console.print(f"[green]バンドル保存:[/green] {bundle_path}")
    console.print("\n[dim]このファイルをnoteに貼り付けて公開してください。[/dim]")


if __name__ == "__main__":
    main()
