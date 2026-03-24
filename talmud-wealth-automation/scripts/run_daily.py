"""
毎日の自動実行スクリプト。
生成 → レビュー → 整形 → noteバンドル出力 を一括で行う。

Usage:
    python scripts/run_daily.py
    python scripts/run_daily.py --theme "手動テーマ"
    python scripts/run_daily.py --skip-x  # X投稿をスキップ

cron 設定例:
    0 5 * * * cd /path/to/talmud-wealth-automation && python scripts/run_daily.py >> logs/cron.log 2>&1
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from app.config import settings
from app.formatter import ContentFormatter
from app.reviewer import ContentReviewer
from app.storage import storage
from app.theme_selector import theme_selector
from app.utils import setup_logger, today_str
from app.writer import get_writer

console = Console()
logger = setup_logger("daily", settings.log_dir())

STEPS = [
    "テーマ選定",
    "Claude生成",
    "ルールチェック",
    "レビュー（API）",
    "整形",
    "保存",
    "noteバンドル出力",
]


@click.command()
@click.option("--theme", "-t", default=None, help="テーマを手動指定")
@click.option("--date", "-d", default=None, help="実行日付（省略時は今日）")
@click.option("--skip-review", is_flag=True, default=False, help="APIレビューをスキップ")
@click.option("--skip-x", is_flag=True, default=False, help="X投稿をスキップ")
@click.option("--gpt", is_flag=True, default=False, help="GPT版も生成する")
def main(
    theme: str | None,
    date: str | None,
    skip_review: bool,
    skip_x: bool,
    gpt: bool,
) -> None:
    date_str = date or today_str()
    console.print(Panel(
        f"[bold]タルムード資産論 — 日次実行[/bold]\n日付: {date_str}",
        style="bold blue",
    ))

    try:
        # 1. テーマ選定
        console.print("\n[bold]1. テーマ選定[/bold]")
        selected_theme = theme_selector.select(manual=theme)
        console.print(f"   → {selected_theme.title}")
        logger.info(f"テーマ: {selected_theme.title}")

        # 2. Claude 生成
        console.print("\n[bold]2. コンテンツ生成（Claude）[/bold]")
        writer = get_writer("claude")
        claude_content = writer.generate(selected_theme.title, selected_theme.source)
        storage.save_content(claude_content, date_str)
        console.print(f"   → X投稿 {claude_content.x_char_count}文字 / 生成完了")

        # GPT版（オプション）
        if gpt:
            console.print("\n[bold]2b. コンテンツ生成（GPT）[/bold]")
            try:
                gpt_writer = get_writer("gpt")
                gpt_content = gpt_writer.generate(selected_theme.title, selected_theme.source)
                storage.save_content(gpt_content, date_str)
                console.print("   → GPT版保存完了")
            except Exception as e:
                console.print(f"   [yellow]GPT生成スキップ: {e}[/yellow]")

        # 3. ルールチェック
        console.print("\n[bold]3. ルールチェック[/bold]")
        rev = ContentReviewer()
        issues = rev.quick_check(claude_content)
        has_issue = any(v for v in issues.values())
        if has_issue:
            for section, items in issues.items():
                for item in items:
                    console.print(f"   [yellow]⚠ {section}: {item}[/yellow]")
        else:
            console.print("   [green]✓ 問題なし[/green]")

        # 4. APIレビュー（オプション）
        review = None
        if not skip_review:
            console.print("\n[bold]4. APIレビュー[/bold]")
            try:
                gpt_content_for_review = storage.load_content(date_str, "gpt") if gpt else None
                review = rev.review(claude_content, compare_with=gpt_content_for_review)
                storage.save_review(review, date_str)
                console.print(f"   → スコア: {review.overall_score:.1f} / 推奨: {review.recommendation.value}")
            except Exception as e:
                console.print(f"   [yellow]APIレビュースキップ: {e}[/yellow]")
                logger.warning(f"APIレビュースキップ: {e}")
        else:
            console.print("\n[bold]4. APIレビュー[/bold] [dim]スキップ[/dim]")

        # 5. 整形
        console.print("\n[bold]5. 整形[/bold]")
        fmt = ContentFormatter()
        try:
            formatted = fmt.format(claude_content)
        except Exception as e:
            console.print(f"   [yellow]API整形失敗 → 軽量整形: {e}[/yellow]")
            text, _, _ = fmt.format_x_only(claude_content.x_post)
            claude_content.x_post = text
            formatted = claude_content

        # 6. 保存
        console.print("\n[bold]6. 保存[/bold]")
        storage.save_final(formatted, date_str)
        x_path = storage.save_x_post(formatted.x_post, date_str)
        fn_path = storage.save_free_note(formatted.free_note_title, formatted.free_note_body, date_str)
        pn_path = storage.save_paid_note(formatted.paid_note_title, formatted.paid_note_body, date_str)
        console.print(f"   X投稿   → {x_path}")
        console.print(f"   無料note → {fn_path}")
        console.print(f"   有料note → {pn_path}")

        # 7. noteバンドル
        console.print("\n[bold]7. noteバンドル出力[/bold]")
        from app.exporter import export_bundle
        bundle_path = export_bundle(formatted, date_str)
        console.print(f"   → {bundle_path}")

        # テーマを使用済みに
        if not theme:
            theme_selector.mark_used(selected_theme)

        console.print(Panel("[bold green]✓ 日次実行 完了[/bold green]", style="green"))
        logger.info(f"日次実行完了: {date_str}")

    except Exception as e:
        console.print(f"\n[red bold]エラーが発生しました: {e}[/red bold]")
        logger.error(f"日次実行エラー: {e}", exc_info=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
