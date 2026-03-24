"""整形モジュール。X投稿の文字数調整とnote Markdownの整形を行う。"""

from __future__ import annotations

from app.config import settings
from app.models import ContentSource, GeneratedContent
from app.utils import extract_json_from_response, setup_logger

logger = setup_logger("formatter", settings.log_dir())


class ContentFormatter:
    """コンテンツの整形を担当する。"""

    def __init__(self) -> None:
        self._client = None
        self._system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        project = settings.load_prompt("project")
        formatter = settings.load_prompt("formatter")
        return f"{project}\n\n---\n\n{formatter}"

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
                key = settings.anthropic_api_key
                if not key:
                    raise ValueError("ANTHROPIC_API_KEY が設定されていません")
                self._client = anthropic.Anthropic(api_key=key)
            except ImportError:
                raise ImportError("anthropic パッケージをインストールしてください")
        return self._client

    def format(self, content: GeneratedContent) -> GeneratedContent:
        """API を使ってコンテンツ全体を整形する。"""
        logger.info(f"整形開始: {content.theme}")

        # まずルールベースでX投稿をチェック
        if content.x_valid:
            logger.info(f"X投稿: {content.x_char_count}文字（OK）")
        else:
            logger.warning(f"X投稿: {content.x_char_count}文字（280文字超過）— API整形を実行")

        client = self._get_client()
        user_message = self._build_user_message(content)

        response = client.messages.create(
            model=settings.generation.get("claude_model", "claude-opus-4-6"),
            max_tokens=4000,
            system=self._system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        result = self._parse_response(response.content[0].text, content)
        logger.info(f"整形完了: X投稿 {result.x_char_count}文字")
        return result

    def format_x_only(self, x_post: str) -> tuple[str, int, bool]:
        """X投稿だけをルールベースで軽量整形する（API不使用）。"""
        text = x_post.strip()
        char_count = len(text)

        # CTA確認・補完
        cta = settings.cta.get("x", "物語と論点はnoteへ。")
        if cta not in text:
            text = text.rstrip() + f"\n\n▶ {cta}"
            char_count = len(text)

        return text, char_count, char_count <= settings.x_max_chars

    def _build_user_message(self, content: GeneratedContent) -> str:
        return f"""## 整形対象コンテンツ

**テーマ**: {content.theme}

### X投稿（{content.x_char_count}文字）
{content.x_post}

### 無料noteタイトル
{content.free_note_title}

### 無料note本文
{content.free_note_body}

### 有料noteタイトル
{content.paid_note_title}

### 有料note本文
{content.paid_note_body}
"""

    def _parse_response(
        self, text: str, original: GeneratedContent
    ) -> GeneratedContent:
        from datetime import datetime
        try:
            data = extract_json_from_response(text)
            return GeneratedContent(
                theme=original.theme,
                source=original.source,
                x_post=data.get("x_post", original.x_post),
                free_note_title=data.get("free_note_title", original.free_note_title),
                free_note_body=data.get("free_note_body", original.free_note_body),
                paid_note_title=data.get("paid_note_title", original.paid_note_title),
                paid_note_body=data.get("paid_note_body", original.paid_note_body),
                notes="\n".join(data.get("changes", [])),
                generation_source=original.generation_source,
                generated_at=datetime.now().isoformat(),
            )
        except Exception as e:
            logger.warning(f"整形レスポンスのパースに失敗しました: {e} — 元データを使用します")
            return original


formatter = ContentFormatter()
