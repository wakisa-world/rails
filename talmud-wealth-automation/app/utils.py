"""汎用ユーティリティ。ログ・日付・テキスト処理など。"""

from __future__ import annotations

import json
import logging
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.logging import RichHandler

console = Console()


def setup_logger(name: str, log_dir: Path, level: str = "INFO") -> logging.Logger:
    """日付付きのファイルログ + コンソールログを設定する。"""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{today_str()}.log"

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        # ファイルハンドラ
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        logger.addHandler(fh)

        # リッチコンソールハンドラ
        ch = RichHandler(console=console, show_path=False)
        ch.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(ch)

    return logger


def today_str() -> str:
    return date.today().isoformat()


def date_slug(d: str | None = None) -> str:
    """'2026-03-25' -> '20260325'"""
    target = d or today_str()
    return target.replace("-", "")


def slug(text: str) -> str:
    """テーマ名をファイル名に使えるスラグに変換する。"""
    import unicodedata
    # 空白をアンダースコアに、制御文字を除去
    cleaned = "".join(c if c.isalnum() or c in "-_" else "_" for c in text)
    return cleaned[:40].strip("_")


def save_json(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_markdown(content: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def extract_json_from_response(text: str) -> dict[str, Any]:
    """LLMレスポンスからJSONブロックを抽出してパースする。"""
    # ```json ... ``` ブロックを優先
    import re
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # フォールバック: テキスト全体をJSONとしてパース
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    raise ValueError("JSONが見つかりませんでした")


def count_chars(text: str) -> int:
    return len(text)
