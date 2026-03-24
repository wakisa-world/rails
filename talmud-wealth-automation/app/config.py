"""設定管理モジュール。settings.yaml と .env を一元管理する。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

# プロジェクトルート
ROOT_DIR = Path(__file__).parent.parent
CONFIG_DIR = ROOT_DIR / "config"
PROMPTS_DIR = ROOT_DIR / "prompts"


def _load_env() -> None:
    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def _load_yaml(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class Settings:
    """settings.yaml + .env をまとめて提供するシングルトン。"""

    _instance: "Settings | None" = None

    def __new__(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        _load_env()
        self._settings = _load_yaml(CONFIG_DIR / "settings.yaml")
        self._prompts = _load_yaml(CONFIG_DIR / "prompts.yaml")
        self._initialized = True

    # --- settings.yaml アクセサ ---

    @property
    def brand(self) -> dict[str, Any]:
        return self._settings.get("brand", {})

    @property
    def content(self) -> dict[str, Any]:
        return self._settings.get("content", {})

    @property
    def generation(self) -> dict[str, Any]:
        return self._settings.get("generation", {})

    @property
    def storage(self) -> dict[str, Any]:
        return self._settings.get("storage", {})

    @property
    def note(self) -> dict[str, Any]:
        return self._settings.get("note", {})

    @property
    def x_config(self) -> dict[str, Any]:
        return self._settings.get("x", {})

    # --- prompts.yaml アクセサ ---

    @property
    def prompts(self) -> dict[str, Any]:
        return self._prompts

    @property
    def forbidden_patterns(self) -> list[str]:
        return self._prompts.get("brand", {}).get("forbidden_patterns", [])

    @property
    def x_max_chars(self) -> int:
        return self._settings.get("content", {}).get("x_max_chars", 280)

    @property
    def cta(self) -> dict[str, str]:
        return self._settings.get("content", {}).get("cta", {})

    # --- 環境変数アクセサ ---

    @property
    def anthropic_api_key(self) -> str | None:
        return os.getenv("ANTHROPIC_API_KEY")

    @property
    def openai_api_key(self) -> str | None:
        return os.getenv("OPENAI_API_KEY")

    @property
    def x_credentials(self) -> dict[str, str | None]:
        return {
            "api_key": os.getenv("X_API_KEY"),
            "api_secret": os.getenv("X_API_SECRET"),
            "access_token": os.getenv("X_ACCESS_TOKEN"),
            "access_token_secret": os.getenv("X_ACCESS_TOKEN_SECRET"),
        }

    @property
    def dry_run(self) -> bool:
        env_val = os.getenv("DRY_RUN", "").lower()
        if env_val in ("false", "0"):
            return False
        if env_val in ("true", "1"):
            return True
        return self.x_config.get("dry_run", True)

    # --- プロンプトファイル読み込み ---

    def load_prompt(self, role: str) -> str:
        path = PROMPTS_DIR / f"{role}_prompt.md"
        if not path.exists():
            raise FileNotFoundError(f"プロンプトファイルが見つかりません: {path}")
        return path.read_text(encoding="utf-8")

    # --- 出力パス ---

    def output_dir(self, sub: str = "") -> Path:
        base = ROOT_DIR / self.storage.get("output_dir", "outputs")
        return base / sub if sub else base

    def review_dir(self) -> Path:
        return ROOT_DIR / self.storage.get("review_dir", "reviews")

    def log_dir(self) -> Path:
        return ROOT_DIR / self.storage.get("log_dir", "logs")

    def theme_dir(self) -> Path:
        return ROOT_DIR / self.storage.get("theme_dir", "data/themes")


# モジュールレベルのシングルトン
settings = Settings()
