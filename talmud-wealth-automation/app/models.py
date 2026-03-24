"""データモデル。dataclass を使ってコンテンツ・テーマ・レビューを表現する。"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any


class ThemeStatus(str, Enum):
    UNUSED = "unused"
    USED = "used"
    PENDING = "pending"


class ContentSource(str, Enum):
    CLAUDE = "claude"
    GPT = "gpt"
    HYBRID = "hybrid"
    MANUAL = "manual"


class ReviewRecommendation(str, Enum):
    CLAUDE_ADOPT = "claude_adopt"
    GPT_ADOPT = "gpt_adopt"
    HYBRID = "hybrid"


@dataclass
class Theme:
    title: str
    source: str = ""
    category: str = ""
    description: str = ""
    status: ThemeStatus = ThemeStatus.UNUSED
    used_date: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Theme":
        d = d.copy()
        d["status"] = ThemeStatus(d.get("status", "unused"))
        return cls(**d)

    @classmethod
    def from_file(cls, path: Path) -> "Theme":
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)


@dataclass
class GeneratedContent:
    theme: str
    source: str
    x_post: str
    free_note_title: str
    free_note_body: str
    paid_note_title: str
    paid_note_body: str
    notes: str = ""
    generation_source: ContentSource = ContentSource.CLAUDE
    generated_at: str = ""

    @property
    def x_char_count(self) -> int:
        return len(self.x_post)

    @property
    def x_valid(self) -> bool:
        return self.x_char_count <= 280

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["generation_source"] = self.generation_source.value
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "GeneratedContent":
        d = d.copy()
        d["generation_source"] = ContentSource(d.get("generation_source", "claude"))
        return cls(**d)

    @classmethod
    def from_json_file(cls, path: Path) -> "GeneratedContent":
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


@dataclass
class ReviewScore:
    overall_score: float
    scores: dict[str, int]
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    improvements: list[dict[str, str]]
    forbidden_check: dict[str, Any]
    recommendation: ReviewRecommendation
    reviewed_source: ContentSource = ContentSource.CLAUDE

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["recommendation"] = self.recommendation.value
        d["reviewed_source"] = self.reviewed_source.value
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ReviewScore":
        d = d.copy()
        d["recommendation"] = ReviewRecommendation(d.get("recommendation", "claude_adopt"))
        d["reviewed_source"] = ContentSource(d.get("reviewed_source", "claude"))
        return cls(**d)


@dataclass
class DailyBundle:
    """1日分のコンテンツ一式。"""
    date: str
    theme: Theme
    claude_content: GeneratedContent | None = None
    gpt_content: GeneratedContent | None = None
    review: ReviewScore | None = None
    final_content: GeneratedContent | None = None

    def adopted_source(self) -> ContentSource:
        if self.review is None:
            return ContentSource.CLAUDE
        rec = self.review.recommendation
        if rec == ReviewRecommendation.GPT_ADOPT:
            return ContentSource.GPT
        return ContentSource.CLAUDE
