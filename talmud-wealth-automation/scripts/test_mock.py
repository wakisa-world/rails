"""
モックテストスクリプト。APIキーなしでフルフロー（生成→整形→保存→バンドル出力）を確認する。

Usage:
    python scripts/test_mock.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date

from rich.console import Console
from rich.panel import Panel

from app.config import settings
from app.exporter import export_bundle
from app.formatter import ContentFormatter
from app.models import ContentSource, GeneratedContent
from app.publisher import XPublisher
from app.reviewer import ContentReviewer
from app.storage import storage
from app.theme_selector import theme_selector
from app.utils import today_str

console = Console()

MOCK_DATE = "2099-01-01"  # テスト用日付（本番と干渉しない）

MOCK_CONTENT = GeneratedContent(
    theme="口約束の重さ――法が許しても、信用は許さない",
    source="バビロニア・タルムード バヴァ・メツィア篇 49a",
    x_post=(
        "法的には正しかった。\n"
        "それでもラビたちは、彼をある言葉で呼んだ。\n\n"
        "商人が口約束をした。\n「明日、この麦を売ろう」と。\n\n"
        "翌日、相場が急騰した。\n商人は「正式な契約はまだだ」と断った。\n\n"
        "法律上、問題はなかった。\nではラビたちはなぜ怒ったのか？\n\n"
        "▶ 物語と論点はnoteへ。"
    ),
    free_note_title="法律的には正しい。でも、なぜラビたちは怒ったのか。――タルムードの「口約束」問題",
    free_note_body=(
        "## はじめに\n\n"
        "「法的に問題はない」という言葉は、ビジネスの現場でよく使われる。\n\n"
        "## 物語\n\n"
        "*出典：バビロニア・タルムード バヴァ・メツィア篇49a*\n\n"
        "ある商人が取引相手に言った。「明日、この麦を届けよう」\n\n"
        "翌朝、相場が急騰。商人は「正式な契約はまだ」と断った。\n\n"
        "ラビたちは言った。「彼は『メフサル・エムナー』だ」\n\n"
        "## 状況整理\n\n"
        "- 法的義務は発生していなかった\n"
        "- 相手は「売ってもらえる」と信じていた\n\n"
        "## 争点\n\n"
        "**争点① 法と道徳は別か**\n\n"
        "**争点② 「約束」はいつ成立するか**\n\n"
        "## あなたへの問い\n\n"
        "「法的にOK」と自分に言い聞かせて動いたことがあるか。\n"
        "口約束を守ることは美徳か、戦略か。\n\n"
        "---\n\nこの話の解釈と、現代の仕事・商売・資産形成への応用は有料noteで深掘りします。"
    ),
    paid_note_title="法の外側で信用は動く――タルムードの「口約束」から学ぶ、長く商売できる人の設計思想",
    paid_note_body=(
        "## この記事で得られること\n\n"
        "- 「法的にOK」と「信用を守る」がなぜ別のことなのか\n"
        "- 信用が積み上がる仕組みの設計思想\n"
        "- 現代の商売・契約・チームで即使える実践ポイント\n\n"
        "## この話の本質\n\n"
        "「メフサル・エムナー」は法的制裁ではない。一種の信用評価だった。\n\n"
        "> **信用とは、義務の外側にある行動によって構築される。**\n\n"
        "## 解釈\n\n"
        "法律は「やってはいけないこと」を定める。"
        "しかし商売における信用は、「やらなくてもいいけどやること」の積み重ねで作られる。\n\n"
        "## 別の見方\n\n"
        "「口約束なら守れないことも当然ある」――確かに。"
        "しかし「理解できる」と「評価される」は別のことだ。\n\n"
        "## 現代への翻訳\n\n"
        "① 「法的にOK」は最低ライン\n\n"
        "② 口頭コミットメントのコスト\n\n"
        "③ 信用の蓄積は義務の外側でしか起きない\n\n"
        "## 実践ポイント\n\n"
        "1. 意思決定の順序を変える\n"
        "2. 口頭コミットメントを記録する\n"
        "3. 断るときのコストを複利で計算する\n\n"
        "## まとめ\n\n"
        "法の外側を意識できる人間は、同じ市場に立っても、見えているものが違う。\n\n"
        "---\n\n明日から使える形に変えることが、このブランドの目的です。"
    ),
    notes="モックデータ",
    generation_source=ContentSource.CLAUDE,
    generated_at="2099-01-01T05:00:00",
)


def run() -> None:
    console.print(Panel("[bold]モックテスト開始[/bold]\n（APIキー不要）", style="cyan"))

    errors: list[str] = []

    # 1. テーマ選定
    console.print("\n[bold]1. テーマ選定[/bold]")
    try:
        theme = theme_selector.select()
        console.print(f"   → {theme.title} [green]✓[/green]")
    except Exception as e:
        console.print(f"   [red]✗ {e}[/red]")
        errors.append(f"テーマ選定: {e}")

    # 2. コンテンツ保存
    console.print("\n[bold]2. コンテンツ保存[/bold]")
    try:
        path = storage.save_content(MOCK_CONTENT, MOCK_DATE)
        console.print(f"   → {path} [green]✓[/green]")
    except Exception as e:
        console.print(f"   [red]✗ {e}[/red]")
        errors.append(f"保存: {e}")

    # 3. ルールチェック
    console.print("\n[bold]3. ルールチェック[/bold]")
    try:
        rev = ContentReviewer()
        issues = rev.quick_check(MOCK_CONTENT)
        has_issue = any(v for v in issues.values())
        if not has_issue:
            console.print("   → 問題なし [green]✓[/green]")
        else:
            for sec, items in issues.items():
                for item in items:
                    console.print(f"   [yellow]⚠ {sec}: {item}[/yellow]")
    except Exception as e:
        console.print(f"   [red]✗ {e}[/red]")
        errors.append(f"ルールチェック: {e}")

    # 4. X投稿検証
    console.print("\n[bold]4. X投稿検証[/bold]")
    try:
        pub = XPublisher(dry_run=True)
        valid, msg = pub.validate(MOCK_CONTENT.x_post)
        console.print(f"   → {msg} [green]✓[/green]")
        result = pub.post(MOCK_CONTENT.x_post)
        console.print(f"   → dry-run: {result['status']} [green]✓[/green]")
    except Exception as e:
        console.print(f"   [red]✗ {e}[/red]")
        errors.append(f"X投稿検証: {e}")

    # 5. 整形（ルールベース）
    console.print("\n[bold]5. 整形（ルールベース）[/bold]")
    try:
        fmt = ContentFormatter()
        text, count, valid = fmt.format_x_only(MOCK_CONTENT.x_post)
        status = "[green]✓[/green]" if valid else "[red]✗[/red]"
        console.print(f"   → X投稿 {count}文字 {status}")
    except Exception as e:
        console.print(f"   [red]✗ {e}[/red]")
        errors.append(f"整形: {e}")

    # 6. ファイル保存一式
    console.print("\n[bold]6. ファイル保存[/bold]")
    try:
        storage.save_final(MOCK_CONTENT, MOCK_DATE)
        storage.save_x_post(MOCK_CONTENT.x_post, MOCK_DATE)
        storage.save_free_note(MOCK_CONTENT.free_note_title, MOCK_CONTENT.free_note_body, MOCK_DATE)
        storage.save_paid_note(MOCK_CONTENT.paid_note_title, MOCK_CONTENT.paid_note_body, MOCK_DATE)
        console.print("   → 全ファイル保存 [green]✓[/green]")
    except Exception as e:
        console.print(f"   [red]✗ {e}[/red]")
        errors.append(f"ファイル保存: {e}")

    # 7. noteバンドル出力
    console.print("\n[bold]7. noteバンドル出力[/bold]")
    try:
        bundle_path = export_bundle(MOCK_CONTENT, MOCK_DATE)
        console.print(f"   → {bundle_path} [green]✓[/green]")
    except Exception as e:
        console.print(f"   [red]✗ {e}[/red]")
        errors.append(f"バンドル出力: {e}")

    # 8. 読み込みテスト
    console.print("\n[bold]8. 読み込みテスト[/bold]")
    try:
        loaded = storage.load_final(MOCK_DATE)
        assert loaded is not None
        assert loaded.theme == MOCK_CONTENT.theme
        console.print("   → 読み込み・検証 [green]✓[/green]")
    except Exception as e:
        console.print(f"   [red]✗ {e}[/red]")
        errors.append(f"読み込みテスト: {e}")

    # 結果
    if not errors:
        console.print(Panel("[bold green]✓ 全テスト通過 — APIキー設定後にrun_daily.pyを実行できます[/bold green]", style="green"))
    else:
        console.print(Panel(
            "[bold red]✗ 一部テスト失敗:[/bold red]\n" + "\n".join(f"  • {e}" for e in errors),
            style="red",
        ))

    console.print(f"\n[dim]テスト出力は outputs/final/{MOCK_DATE.replace('-','')}*.* に保存されました[/dim]")


if __name__ == "__main__":
    run()
