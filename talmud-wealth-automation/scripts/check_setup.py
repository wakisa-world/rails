"""
セットアップ確認スクリプト。
環境変数・設定・依存関係が揃っているか確認する。

Usage:
    python scripts/check_setup.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

ROOT = Path(__file__).parent.parent


def check_files() -> list[tuple[str, bool, str]]:
    required = [
        ("config/settings.yaml", "ブランド設定"),
        ("config/prompts.yaml", "品質基準"),
        ("prompts/project_prompt.md", "ブランド方針"),
        ("prompts/writer_prompt.md", "ライタープロンプト"),
        ("prompts/reviewer_prompt.md", "レビュープロンプト"),
        ("prompts/formatter_prompt.md", "整形プロンプト"),
        (".env", "API設定"),
    ]
    results = []
    for rel, label in required:
        path = ROOT / rel
        exists = path.exists()
        note = "" if exists else ("【重要】" if "env" in rel else "")
        results.append((label, exists, note))
    return results


def check_env() -> list[tuple[str, bool, str]]:
    import os
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")

    keys = [
        ("ANTHROPIC_API_KEY", "Claude生成・レビュー・整形", True),
        ("OPENAI_API_KEY", "GPT比較（任意）", False),
        ("X_API_KEY", "X投稿", False),
        ("X_API_SECRET", "X投稿", False),
        ("X_ACCESS_TOKEN", "X投稿", False),
        ("X_ACCESS_TOKEN_SECRET", "X投稿", False),
    ]
    results = []
    for key, usage, required in keys:
        val = os.getenv(key)
        ok = bool(val)
        note = "必須" if required else "任意"
        results.append((key, ok, f"{usage} [{note}]"))
    return results


def check_packages() -> list[tuple[str, bool, str]]:
    packages = [
        ("anthropic", "Claude API"),
        ("openai", "GPT API"),
        ("tweepy", "X API"),
        ("dotenv", "python-dotenv"),
        ("yaml", "pyyaml"),
        ("click", "CLI"),
        ("rich", "ターミナル表示"),
    ]
    results = []
    for pkg, label in packages:
        try:
            __import__(pkg)
            results.append((label, True, ""))
        except ImportError:
            results.append((label, False, f"pip install {pkg}"))
    return results


def check_themes() -> tuple[int, int]:
    from app.theme_selector import theme_selector
    summary = theme_selector.list_summary()
    return summary["total"], summary["unused"]


def main() -> None:
    console.print(Panel("[bold]タルムード資産論 — セットアップ確認[/bold]", style="blue"))

    all_ok = True

    # ファイル確認
    file_results = check_files()
    table = Table(title="必須ファイル", show_header=True)
    table.add_column("ファイル")
    table.add_column("状態", width=6)
    table.add_column("メモ")
    for label, ok, note in file_results:
        icon = "[green]✓[/green]" if ok else "[red]✗[/red]"
        if not ok:
            all_ok = False
        table.add_row(label, icon, note)
    console.print(table)

    # 環境変数確認
    env_results = check_env()
    table2 = Table(title="環境変数", show_header=True)
    table2.add_column("変数名")
    table2.add_column("状態", width=6)
    table2.add_column("用途")
    for key, ok, usage in env_results:
        icon = "[green]✓[/green]" if ok else "[yellow]—[/yellow]"
        if not ok and "必須" in usage:
            all_ok = False
        table2.add_row(key, icon, usage)
    console.print(table2)

    # パッケージ確認
    pkg_results = check_packages()
    table3 = Table(title="Pythonパッケージ", show_header=True)
    table3.add_column("パッケージ")
    table3.add_column("状態", width=6)
    table3.add_column("インストール方法")
    for label, ok, hint in pkg_results:
        icon = "[green]✓[/green]" if ok else "[red]✗[/red]"
        if not ok:
            all_ok = False
        table3.add_row(label, icon, hint)
    console.print(table3)

    # テーマ確認
    try:
        total, unused = check_themes()
        color = "green" if unused > 0 else "red"
        console.print(f"\nテーマ: 合計 {total}件 / [{color}]未使用 {unused}件[/{color}]")
        if unused == 0:
            console.print("[yellow]⚠ 未使用テーマがありません。manage_themes.py add で追加してください。[/yellow]")
    except Exception as e:
        console.print(f"[red]テーマ確認エラー: {e}[/red]")

    # 総合判定
    if all_ok:
        console.print(Panel("[bold green]✓ セットアップ完了。run_daily.py を実行できます。[/bold green]", style="green"))
    else:
        console.print(Panel("[bold yellow]⚠ 設定が不完全です。上記を確認してください。[/bold yellow]", style="yellow"))


if __name__ == "__main__":
    main()
