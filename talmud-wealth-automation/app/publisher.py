"""X投稿モジュール。Tweepy を使ってXに投稿する。dry-run 対応。"""

from __future__ import annotations

from app.config import settings
from app.utils import setup_logger

logger = setup_logger("publisher", settings.log_dir())


class XPublisher:
    """X（Twitter）への投稿を担当する。"""

    def __init__(self, dry_run: bool | None = None) -> None:
        self.dry_run = dry_run if dry_run is not None else settings.dry_run
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import tweepy
            except ImportError:
                raise ImportError("tweepy パッケージをインストールしてください: pip install tweepy")

            creds = settings.x_credentials
            missing = [k for k, v in creds.items() if not v]
            if missing:
                raise ValueError(f"X API認証情報が不足しています: {missing}")

            self._client = tweepy.Client(
                consumer_key=creds["api_key"],
                consumer_secret=creds["api_secret"],
                access_token=creds["access_token"],
                access_token_secret=creds["access_token_secret"],
            )
        return self._client

    def post(self, text: str) -> dict[str, str]:
        """X に投稿する。dry_run=True の場合は投稿しない。"""
        char_count = len(text)

        if char_count > 280:
            raise ValueError(f"投稿文字数が280文字を超えています（{char_count}文字）")

        if self.dry_run:
            logger.info(f"[DRY-RUN] 投稿内容（{char_count}文字）:\n{text}")
            return {"status": "dry_run", "text": text, "char_count": str(char_count)}

        try:
            client = self._get_client()
            response = client.create_tweet(text=text)
            tweet_id = str(response.data["id"])
            logger.info(f"投稿成功: tweet_id={tweet_id}")
            return {"status": "success", "tweet_id": tweet_id, "char_count": str(char_count)}
        except Exception as e:
            logger.error(f"投稿失敗: {e}")
            return {"status": "error", "error": str(e)}

    def validate(self, text: str) -> tuple[bool, str]:
        """投稿前の検証。(valid, message) を返す。"""
        count = len(text)
        if count > 280:
            return False, f"280文字を超えています（{count}文字）"
        if not text.strip():
            return False, "本文が空です"
        return True, f"OK（{count}文字）"


publisher = XPublisher()
