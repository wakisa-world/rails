"""コンテンツ生成モジュール。Claude / GPT を呼び出してコンテンツを生成する。"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from app.config import settings
from app.models import ContentSource, GeneratedContent
from app.utils import extract_json_from_response, setup_logger

logger = setup_logger("writer", settings.log_dir())


class BaseWriter:
    """ライターの基底クラス。"""

    def __init__(self) -> None:
        self._system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        project = settings.load_prompt("project")
        writer = settings.load_prompt("writer")
        return f"{project}\n\n---\n\n{writer}"

    def generate(self, theme: str, source: str = "") -> GeneratedContent:
        raise NotImplementedError

    def _parse_response(self, text: str, source: ContentSource) -> GeneratedContent:
        data = extract_json_from_response(text)
        return GeneratedContent(
            theme=data.get("theme", ""),
            source=data.get("source", ""),
            x_post=data.get("x_post", ""),
            free_note_title=data.get("free_note_title", ""),
            free_note_body=data.get("free_note_body", ""),
            paid_note_title=data.get("paid_note_title", ""),
            paid_note_body=data.get("paid_note_body", ""),
            notes=data.get("notes", ""),
            generation_source=source,
            generated_at=datetime.now().isoformat(),
        )


class ClaudeWriter(BaseWriter):
    """Anthropic Claude を使ってコンテンツを生成する。"""

    def __init__(self) -> None:
        super().__init__()
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
                key = settings.anthropic_api_key
                if not key:
                    raise ValueError("ANTHROPIC_API_KEY が設定されていません")
                self._client = anthropic.Anthropic(api_key=key)
            except ImportError:
                raise ImportError("anthropic パッケージをインストールしてください: pip install anthropic")
        return self._client

    def generate(self, theme: str, source: str = "") -> GeneratedContent:
        logger.info(f"Claude でコンテンツ生成開始: {theme}")
        client = self._get_client()
        gen_cfg = settings.generation

        user_message = f"テーマ: {theme}"
        if source:
            user_message += f"\n出典: {source}"

        response = client.messages.create(
            model=gen_cfg.get("claude_model", "claude-opus-4-6"),
            max_tokens=gen_cfg.get("max_tokens", 4000),
            system=self._system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        content_text = response.content[0].text
        result = self._parse_response(content_text, ContentSource.CLAUDE)
        logger.info(f"Claude 生成完了: X投稿 {result.x_char_count}文字")
        return result


class GPTWriter(BaseWriter):
    """OpenAI GPT を使ってコンテンツを生成する（比較用）。"""

    def __init__(self) -> None:
        super().__init__()
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import openai
                key = settings.openai_api_key
                if not key:
                    raise ValueError("OPENAI_API_KEY が設定されていません")
                self._client = openai.OpenAI(api_key=key)
            except ImportError:
                raise ImportError("openai パッケージをインストールしてください: pip install openai")
        return self._client

    def generate(self, theme: str, source: str = "") -> GeneratedContent:
        logger.info(f"GPT でコンテンツ生成開始: {theme}")
        client = self._get_client()
        gen_cfg = settings.generation

        user_message = f"テーマ: {theme}"
        if source:
            user_message += f"\n出典: {source}"

        response = client.chat.completions.create(
            model=gen_cfg.get("gpt_model", "gpt-4o"),
            max_tokens=gen_cfg.get("max_tokens", 4000),
            temperature=gen_cfg.get("temperature", 0.7),
            messages=[
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": user_message},
            ],
        )

        content_text = response.choices[0].message.content
        result = self._parse_response(content_text, ContentSource.GPT)
        logger.info(f"GPT 生成完了: X投稿 {result.x_char_count}文字")
        return result


def get_writer(source: str = "claude") -> BaseWriter:
    """source に応じたライターを返す。"""
    if source == "gpt":
        return GPTWriter()
    return ClaudeWriter()
