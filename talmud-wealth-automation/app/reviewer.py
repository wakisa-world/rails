"""レビューモジュール。生成コンテンツをブランド方針に照らして評価する。"""

from __future__ import annotations

from app.config import settings
from app.models import ContentSource, GeneratedContent, ReviewRecommendation, ReviewScore
from app.utils import extract_json_from_response, setup_logger

logger = setup_logger("reviewer", settings.log_dir())


class ContentReviewer:
    """Claude を使ってコンテンツのレビューを行う。"""

    def __init__(self) -> None:
        self._client = None
        self._system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        project = settings.load_prompt("project")
        reviewer = settings.load_prompt("reviewer")
        return f"{project}\n\n---\n\n{reviewer}"

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

    def review(
        self,
        content: GeneratedContent,
        compare_with: GeneratedContent | None = None,
    ) -> ReviewScore:
        """コンテンツをレビューする。compare_with があれば比較レビューを行う。"""
        logger.info(f"レビュー開始: {content.theme}")
        client = self._get_client()

        user_message = self._build_user_message(content, compare_with)

        response = client.messages.create(
            model=settings.generation.get("claude_model", "claude-opus-4-6"),
            max_tokens=2000,
            system=self._system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        result = self._parse_response(response.content[0].text, content.generation_source)
        logger.info(f"レビュー完了: スコア {result.overall_score:.1f} / 推奨 {result.recommendation.value}")
        return result

    def quick_check(self, content: GeneratedContent) -> dict[str, list[str]]:
        """API呼び出しなしでルールベースの即時チェックを行う。"""
        issues: dict[str, list[str]] = {"x_post": [], "free_note": [], "paid_note": [], "brand": []}

        # X投稿チェック
        if content.x_char_count > 280:
            issues["x_post"].append(f"280文字超過（{content.x_char_count}文字）")
        if "note" not in content.x_post.lower():
            issues["x_post"].append("note導線がありません")
        if "？" not in content.x_post and "?" not in content.x_post:
            issues["x_post"].append("問いかけが含まれていません")

        # 無料note
        cfg = settings.prompts.get("free_note", {})
        min_len = cfg.get("min_length", 600)
        if len(content.free_note_body) < min_len:
            issues["free_note"].append(f"本文が短すぎます（{len(content.free_note_body)}文字）")
        if "有料" not in content.free_note_body:
            issues["free_note"].append("有料noteへの導線がありません")

        # 有料note
        cfg_paid = settings.prompts.get("paid_note", {})
        min_len_paid = cfg_paid.get("min_length", 1000)
        if len(content.paid_note_body) < min_len_paid:
            issues["paid_note"].append(f"本文が短すぎます（{len(content.paid_note_body)}文字）")

        # ブランド禁止パターン
        all_text = " ".join([content.x_post, content.free_note_body, content.paid_note_body])
        for pattern in settings.forbidden_patterns:
            if pattern in all_text:
                issues["brand"].append(f"禁止表現「{pattern}」が含まれています")

        return issues

    def _build_user_message(
        self, content: GeneratedContent, compare: GeneratedContent | None
    ) -> str:
        msg = f"## レビュー対象（Claude版）\n\n"
        msg += f"**テーマ**: {content.theme}\n\n"
        msg += f"### X投稿\n{content.x_post}\n\n"
        msg += f"### 無料noteタイトル\n{content.free_note_title}\n\n"
        msg += f"### 無料note本文\n{content.free_note_body}\n\n"
        msg += f"### 有料noteタイトル\n{content.paid_note_title}\n\n"
        msg += f"### 有料note本文\n{content.paid_note_body}\n"

        if compare:
            msg += f"\n---\n\n## 比較対象（GPT版）\n\n"
            msg += f"### X投稿\n{compare.x_post}\n\n"
            msg += f"### 無料note本文\n{compare.free_note_body}\n\n"
            msg += f"### 有料note本文\n{compare.paid_note_body}\n"

        return msg

    def _parse_response(
        self, text: str, reviewed_source: ContentSource
    ) -> ReviewScore:
        data = extract_json_from_response(text)
        return ReviewScore(
            overall_score=float(data.get("overall_score", 0)),
            scores=data.get("scores", {}),
            summary=data.get("summary", ""),
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            improvements=data.get("improvements", []),
            forbidden_check=data.get("forbidden_check", {"passed": True, "issues": []}),
            recommendation=ReviewRecommendation(
                data.get("recommendation", "claude_adopt")
            ),
            reviewed_source=reviewed_source,
        )


reviewer = ContentReviewer()
