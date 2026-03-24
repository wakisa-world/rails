"""ファイル保存・読み込み管理。日付/テーマ別にコンテンツを整理する。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.config import settings
from app.models import GeneratedContent, ReviewScore
from app.utils import date_slug, save_json, save_markdown, slug, today_str


class Storage:
    """outputs/ reviews/ へのファイル操作を担当する。"""

    def content_path(self, date_str: str, source: str, ext: str = "json") -> Path:
        d = date_slug(date_str)
        return settings.output_dir() / source / f"{d}.{ext}"

    def final_path(self, date_str: str) -> Path:
        d = date_slug(date_str)
        return settings.output_dir("final") / f"{d}.json"

    def x_path(self, date_str: str) -> Path:
        d = date_slug(date_str)
        return settings.output_dir("x") / f"{d}.txt"

    def free_note_path(self, date_str: str) -> Path:
        d = date_slug(date_str)
        return settings.output_dir("free_note") / f"{d}.md"

    def paid_note_path(self, date_str: str) -> Path:
        d = date_slug(date_str)
        return settings.output_dir("paid_note") / f"{d}.md"

    def review_path(self, date_str: str) -> Path:
        d = date_slug(date_str)
        return settings.review_dir() / f"{d}_review.json"

    def bundle_path(self, date_str: str) -> Path:
        d = date_slug(date_str)
        return settings.output_dir("final") / f"{d}_bundle.md"

    # --- 保存 ---

    def save_content(self, content: GeneratedContent, date_str: str | None = None) -> Path:
        date_str = date_str or today_str()
        source = content.generation_source.value
        path = self.content_path(date_str, source)
        save_json(content.to_dict(), path)
        return path

    def save_final(self, content: GeneratedContent, date_str: str | None = None) -> Path:
        date_str = date_str or today_str()
        path = self.final_path(date_str)
        save_json(content.to_dict(), path)
        return path

    def save_x_post(self, text: str, date_str: str | None = None) -> Path:
        date_str = date_str or today_str()
        path = self.x_path(date_str)
        save_markdown(text, path)
        return path

    def save_free_note(self, title: str, body: str, date_str: str | None = None) -> Path:
        date_str = date_str or today_str()
        path = self.free_note_path(date_str)
        md = f"# {title}\n\n{body}\n"
        save_markdown(md, path)
        return path

    def save_paid_note(self, title: str, body: str, date_str: str | None = None) -> Path:
        date_str = date_str or today_str()
        path = self.paid_note_path(date_str)
        md = f"# {title}\n\n{body}\n"
        save_markdown(md, path)
        return path

    def save_review(self, review: ReviewScore, date_str: str | None = None) -> Path:
        date_str = date_str or today_str()
        path = self.review_path(date_str)
        save_json(review.to_dict(), path)
        return path

    # --- 読み込み ---

    def load_content(self, date_str: str, source: str = "claude") -> GeneratedContent | None:
        path = self.content_path(date_str, source)
        if not path.exists():
            return None
        with open(path, encoding="utf-8") as f:
            return GeneratedContent.from_dict(json.load(f))

    def load_final(self, date_str: str) -> GeneratedContent | None:
        path = self.final_path(date_str)
        if not path.exists():
            return None
        with open(path, encoding="utf-8") as f:
            return GeneratedContent.from_dict(json.load(f))

    def load_review(self, date_str: str) -> ReviewScore | None:
        path = self.review_path(date_str)
        if not path.exists():
            return None
        with open(path, encoding="utf-8") as f:
            return ReviewScore.from_dict(json.load(f))

    def exists_final(self, date_str: str) -> bool:
        return self.final_path(date_str).exists()


storage = Storage()
