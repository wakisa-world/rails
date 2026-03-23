#!/bin/bash
# ============================================================
# init.sh — AI経済圏の創世 初期化スクリプト
# 初回セットアップ時に1回だけ実行する
# 使い方: ./scripts/init.sh
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================"
echo "  AI経済圏の創世 — 初期化"
echo "============================================"

# --- ディレクトリ作成 ---
echo "[1/3] ディレクトリを作成..."
mkdir -p \
  "$ROOT_DIR/agents" \
  "$ROOT_DIR/prompts" \
  "$ROOT_DIR/scripts" \
  "$ROOT_DIR/data/daily_logs" \
  "$ROOT_DIR/data/notion_exports" \
  "$ROOT_DIR/data/product_ideas" \
  "$ROOT_DIR/data/weekly_reviews" \
  "$ROOT_DIR/data/context" \
  "$ROOT_DIR/docs"
echo "  ✓ ディレクトリ作成完了"

# --- コンテキストファイル初期化 ---
echo "[2/3] コンテキストファイルを初期化..."

PREV_LOG="$ROOT_DIR/data/context/previous_log.json"
GOOD_THEMES="$ROOT_DIR/data/context/good_themes.md"
BAD_THEMES="$ROOT_DIR/data/context/bad_themes.md"
FOCUS_THEME="$ROOT_DIR/data/context/focus_theme.md"

if [ ! -f "$PREV_LOG" ]; then
  echo "null" > "$PREV_LOG"
  echo "  ✓ previous_log.json を初期化"
fi

if [ ! -f "$GOOD_THEMES" ]; then
  cat > "$GOOD_THEMES" << 'EOF'
# 反応が良かったテーマ

このファイルには、X投稿で反応が良かったテーマや切り口を記録する。
週次レビュー後に手動で追記してください。

## 書き方
- テーマ名：説明（実験日）

## 記録
（まだ記録なし）
EOF
  echo "  ✓ good_themes.md を初期化"
fi

if [ ! -f "$BAD_THEMES" ]; then
  cat > "$BAD_THEMES" << 'EOF'
# 反応が悪かったテーマ

このファイルには、反応が薄かった・避けるべきテーマを記録する。
週次レビュー後に手動で追記してください。

## 書き方
- テーマ名：なぜ避けるか（実験日）

## 記録
（まだ記録なし）
EOF
  echo "  ✓ bad_themes.md を初期化"
fi

if [ ! -f "$FOCUS_THEME" ]; then
  cat > "$FOCUS_THEME" << 'EOF'
# 今日の重点テーマ

このファイルに今日の実験で優先して扱うテーマを書く。
人間が手動で設定する。空でもよい。

## 書き方
テーマの1文説明を書くだけでよい。

## 現在の重点テーマ
（未設定）
EOF
  echo "  ✓ focus_theme.md を初期化"
fi

# --- スクリプトに実行権限を付与 ---
echo "[3/3] 実行権限を付与..."
chmod +x "$ROOT_DIR/scripts/"*.sh
chmod +x "$ROOT_DIR/scripts/"*.py 2>/dev/null || true
echo "  ✓ 実行権限付与完了"

echo ""
echo "============================================"
echo "  初期化完了"
echo "============================================"
echo ""
echo "次のステップ："
echo "  1. （任意）data/context/focus_theme.md に今日の重点テーマを書く"
echo "  2. 日次実験を実行する："
echo "     ./scripts/run_daily.sh"
echo ""
echo "Claude Code から実行する場合："
echo "  Claude Code を開いて「今日の日次実験を実行して」と伝える"
echo ""
