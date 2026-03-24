"""テーマ選定モジュール。data/themes/ からその日のテーマを選ぶ。"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from app.config import settings
from app.models import Theme, ThemeStatus
from app.utils import today_str


class ThemeSelector:
    """テーマ候補の管理と選定を行う。"""

    def __init__(self) -> None:
        self.theme_dir = settings.theme_dir()
        self.theme_dir.mkdir(parents=True, exist_ok=True)

    def all_themes(self) -> list[Theme]:
        themes = []
        for path in sorted(self.theme_dir.glob("*.json")):
            try:
                themes.append(Theme.from_file(path))
            except Exception:
                pass
        return themes

    def unused_themes(self) -> list[Theme]:
        return [t for t in self.all_themes() if t.status == ThemeStatus.UNUSED]

    def select(self, manual: str | None = None) -> Theme:
        """テーマを選ぶ。manual が指定されれば優先使用。"""
        if manual:
            return Theme(title=manual, status=ThemeStatus.UNUSED)

        unused = self.unused_themes()
        if not unused:
            raise ValueError(
                "未使用のテーマがありません。data/themes/ にテーマJSONを追加してください。"
            )
        return random.choice(unused)

    def mark_used(self, theme: Theme) -> None:
        """テーマを使用済みにする。"""
        theme.status = ThemeStatus.USED
        theme.used_date = today_str()
        path = self.theme_dir / f"{self._theme_filename(theme.title)}.json"
        if path.exists():
            theme.save(path)

    def add_theme(self, theme: Theme) -> Path:
        """新しいテーマをファイルに追加する。"""
        filename = self._theme_filename(theme.title)
        path = self.theme_dir / f"{filename}.json"
        theme.save(path)
        return path

    def _theme_filename(self, title: str) -> str:
        from app.utils import slug
        return slug(title) or "theme"

    def list_summary(self) -> dict[str, int]:
        all_t = self.all_themes()
        return {
            "total": len(all_t),
            "unused": sum(1 for t in all_t if t.status == ThemeStatus.UNUSED),
            "used": sum(1 for t in all_t if t.status == ThemeStatus.USED),
            "pending": sum(1 for t in all_t if t.status == ThemeStatus.PENDING),
        }


theme_selector = ThemeSelector()
