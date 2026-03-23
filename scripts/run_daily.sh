#!/bin/bash
# ============================================================
# run_daily.sh — AI経済圏の創世 日次実験実行スクリプト
# 使い方: ./scripts/run_daily.sh
#         ./scripts/run_daily.sh 2026-03-25  (日付指定)
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# --- 日付設定 ---
if [ -n "$1" ]; then
  DATE="$1"
else
  DATE=$(TZ=Asia/Tokyo date +%Y-%m-%d)
fi

echo "============================================"
echo "  AI経済圏の創世 — 日次実験"
echo "  実行日: $DATE"
echo "============================================"

# --- ディレクトリ確認・作成 ---
mkdir -p \
  "$ROOT_DIR/data/daily_logs" \
  "$ROOT_DIR/data/notion_exports" \
  "$ROOT_DIR/data/product_ideas" \
  "$ROOT_DIR/data/weekly_reviews" \
  "$ROOT_DIR/data/context"

# --- コンテキストファイル初期化 ---
PREV_LOG="$ROOT_DIR/data/context/previous_log.json"
GOOD_THEMES="$ROOT_DIR/data/context/good_themes.md"
BAD_THEMES="$ROOT_DIR/data/context/bad_themes.md"
FOCUS_THEME="$ROOT_DIR/data/context/focus_theme.md"

[ ! -f "$PREV_LOG" ]    && echo "null" > "$PREV_LOG"
[ ! -f "$GOOD_THEMES" ] && echo "# 反応が良かったテーマ\n（まだ記録なし）" > "$GOOD_THEMES"
[ ! -f "$BAD_THEMES" ]  && echo "# 反応が悪かったテーマ\n（まだ記録なし）" > "$BAD_THEMES"
[ ! -f "$FOCUS_THEME" ] && echo "（重点テーマ未設定）" > "$FOCUS_THEME"

# --- 出力ファイルパス ---
JSON_OUT="$ROOT_DIR/data/daily_logs/$DATE.json"
NOTION_OUT="$ROOT_DIR/data/notion_exports/$DATE.md"
PRODUCT_OUT="$ROOT_DIR/data/product_ideas/$DATE.md"

# --- 重複チェック ---
if [ -f "$JSON_OUT" ]; then
  echo "[警告] $DATE のログが既に存在します: $JSON_OUT"
  echo "上書きしますか？ (y/N)"
  read -r ANSWER
  if [ "$ANSWER" != "y" ] && [ "$ANSWER" != "Y" ]; then
    echo "実行をキャンセルしました。"
    exit 0
  fi
fi

# --- プロンプト組み立て ---
echo "[1/5] プロンプトを組み立て中..."

PREV_LOG_CONTENT=$(cat "$PREV_LOG" 2>/dev/null || echo "null")
GOOD_THEMES_CONTENT=$(cat "$GOOD_THEMES" 2>/dev/null || echo "記載なし")
BAD_THEMES_CONTENT=$(cat "$BAD_THEMES" 2>/dev/null || echo "記載なし")
FOCUS_THEME_CONTENT=$(cat "$FOCUS_THEME" 2>/dev/null || echo "記載なし")

TEMPLATE=$(cat "$ROOT_DIR/prompts/daily_system_prompt.md")

# プレースホルダー置換
PROMPT="${TEMPLATE//\{\{DATE\}\}/$DATE}"
PROMPT="${PROMPT//\{\{PREVIOUS_LOG\}\}/$PREV_LOG_CONTENT}"
PROMPT="${PROMPT//\{\{GOOD_THEMES\}\}/$GOOD_THEMES_CONTENT}"
PROMPT="${PROMPT//\{\{BAD_THEMES\}\}/$BAD_THEMES_CONTENT}"
PROMPT="${PROMPT//\{\{FOCUS_THEME\}\}/$FOCUS_THEME_CONTENT}"

# --- Claude CLI で実行 ---
echo "[2/5] Claude に実験を実行させています..."

if ! command -v claude &> /dev/null; then
  echo ""
  echo "[エラー] claude コマンドが見つかりません。"
  echo ""
  echo "以下のいずれかで実行してください："
  echo ""
  echo "  方法1: Claude Code を開いて「今日の日次実験を実行して」と伝える"
  echo "  方法2: claude CLI をインストールして再実行する"
  echo "         https://docs.anthropic.com/claude-code"
  echo ""
  exit 1
fi

# Claude CLIで実行（JSONのみ出力させる）
RAW_OUTPUT=$(claude --print -p "$PROMPT" 2>/dev/null)

# JSONブロックを抽出
JSON_CONTENT=$(echo "$RAW_OUTPUT" | python3 -c "
import sys, re
text = sys.stdin.read()
# コードブロックから抽出
match = re.search(r'\`\`\`json\s*(.*?)\`\`\`', text, re.DOTALL)
if match:
    print(match.group(1).strip())
else:
    # コードブロックがなければそのまま（JSONらしい部分を抽出）
    match2 = re.search(r'\{.*\}', text, re.DOTALL)
    if match2:
        print(match2.group(0).strip())
    else:
        print(text.strip())
" 2>/dev/null)

# --- JSON検証・保存 ---
echo "[3/5] 結果を保存しています..."

if echo "$JSON_CONTENT" | python3 -m json.tool > /dev/null 2>&1; then
  echo "$JSON_CONTENT" > "$JSON_OUT"
  echo "  ✓ JSON保存: $JSON_OUT"
else
  echo "[警告] JSON形式が不正です。生の出力を保存します。"
  FALLBACK_FILE="$ROOT_DIR/data/daily_logs/${DATE}_raw.txt"
  echo "$RAW_OUTPUT" > "$FALLBACK_FILE"
  echo "  生出力保存先: $FALLBACK_FILE"
  echo "  手動で確認・修正してください。"
  exit 1
fi

# --- Notion MD・商品案MD を生成 ---
echo "[4/5] Markdownファイルを生成しています..."

python3 "$SCRIPT_DIR/export_notion.py" "$JSON_OUT" "$NOTION_OUT"
echo "  ✓ Notion用MD: $NOTION_OUT"

python3 "$SCRIPT_DIR/export_product.py" "$JSON_OUT" "$PRODUCT_OUT"
echo "  ✓ 商品案ストック: $PRODUCT_OUT"

# --- コンテキスト更新 ---
echo "[5/5] コンテキストを更新しています..."
cp "$JSON_OUT" "$PREV_LOG"
echo "  ✓ previous_log.json を更新"

# --- 結果サマリー表示 ---
echo ""
echo "============================================"
echo "  実験完了 — $DATE"
echo "============================================"

# 採用投稿を表示
python3 - "$JSON_OUT" <<'PYEOF'
import json, sys
with open(sys.argv[1]) as f:
    d = json.load(f)
idx = d.get("selected_post_index", 0)
post = d["x_posts"][idx]
product = d["product_idea"]
print(f"\n【採用投稿】（{post['type']}）")
print(f"  {post['hook']}")
print(f"  {post['body']}")
print(f"\n【商品案タイトル】")
print(f"  {product['title']}（スコア: {product['score']}点）")
print(f"\n【明日の改善仮説】")
print(f"  {d['tomorrow_hypothesis']}")
print(f"\n【保存ファイル】")
print(f"  {sys.argv[1]}")
PYEOF

echo ""
echo "  data/notion_exports/$DATE.md"
echo "  data/product_ideas/$DATE.md"
echo ""
echo "次のステップ："
echo "  1. X投稿の文字数をXの入力画面で確認する"
echo "  2. 採用投稿を実際にXに投稿する（手動）"
echo "  3. 商品案をnote等で実際に作成する（任意）"
echo ""
