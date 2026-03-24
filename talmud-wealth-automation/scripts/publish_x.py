"""
X投稿スクリプト。

Usage:
    python scripts/publish_x.py --date 2026-03-25 --dry-run
    python scripts/publish_x.py --date 2026-03-25
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from rich.console import Console
from rich.panel import Panel

from app.config import settings
from app.publisher import XPublisher
from app.storage import storage
from app.utils import save_json, setup_logger, today_str

console = Console()
logger = setup_logger("publish", settings.log_dir())


@click.command()
@click.option("--date", "-d", default=None, help="投稿対象日付 (YYYY-MM-DD)")
@click.option("--dry-run", is_flag=True, default=None, help="投稿せず内容を確認するだけ")
def main(date: str | None, dry_run: bool | None) -> None:
    date_str = date or today_str()

    # dry_run は CLI フラグ > .env/settings の順で決定
    use_dry_run = dry_run if dry_run is not None else settings.dry_run
    mode = "[DRY-RUN]" if use_dry_run else "[本番投稿]"

    console.print(Panel(f"[bold]タルムード資産論 — X投稿 {mode}[/bold]\n日付: {date_str}", style="blue"))

    # 投稿文を読み込む
    x_path = storage.x_path(date_str)
    if not x_path.exists():
        console.print(f"[red]X投稿ファイルが見つかりません: {x_path}[/red]")
        console.print("先に format_content.py を実行してください")
        raise SystemExit(1)

    text = x_path.read_text(encoding="utf-8").strip()

    # 検証
    pub = XPublisher(dry_run=use_dry_run)
    valid, msg = pub.validate(text)
    if not valid:
        console.print(f"[red]検証エラー: {msg}[/red]")
        raise SystemExit(1)

    # 投稿内容表示
    console.print(Panel(f"{text}\n\n{msg}", title="投稿内容"))

    if not use_dry_run:
        confirm = click.confirm("本当に投稿しますか？", default=False)
        if not confirm:
            console.print("[yellow]キャンセルしました[/yellow]")
            raise SystemExit(0)

    # 投稿実行
    result = pub.post(text)

    # ログ保存
    log_path = settings.log_dir() / f"{date_str}_x_publish.json"
    save_json({**result, "date": date_str, "dry_run": use_dry_run}, log_path)

    if result["status"] in ("success", "dry_run"):
        console.print(f"[green]{mode} 完了[/green]")
        if result.get("tweet_id"):
            console.print(f"tweet_id: {result['tweet_id']}")
    else:
        console.print(f"[red]投稿エラー: {result.get('error')}[/red]")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
