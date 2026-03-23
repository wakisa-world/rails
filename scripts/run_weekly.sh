#!/bin/bash
# ============================================================
# run_weekly.sh — AI経済圏の創世 週次レビュー実行スクリプト
# 使い方: ./scripts/run_weekly.sh
#         ./scripts/run_weekly.sh 2026-03-16 2026-03-22  (期間指定)
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# --- 期間設定 ---
if [ -n "$2" ]; then
  DATE_FROM="$1"
  DATE_TO="$2"
else
  # 直近7日間
  DATE_TO=$(TZ=Asia/Tokyo date +%Y-%m-%d)
  DATE_FROM=$(TZ=Asia/Tokyo date -d "7 days ago" +%Y-%m-%d 2>/dev/null || \
              TZ=Asia/Tokyo date -v-7d +%Y-%m-%d 2>/dev/null || \
              echo "")
  if [ -z "$DATE_FROM" ]; then
    echo "[エラー] 日付計算に失敗しました。期間を手動で指定してください。"
    echo "  例: ./scripts/run_weekly.sh 2026-03-16 2026-03-22"
    exit 1
  fi
fi

# 週番号
YEAR=$(echo "$DATE_TO" | cut -d'-' -f1)
WEEK_NUM=$(TZ=Asia/Tokyo date -d "$DATE_TO" +%V 2>/dev/null || \
           TZ=Asia/Tokyo date -j -f "%Y-%m-%d" "$DATE_TO" +%V 2>/dev/null || \
           echo "XX")
WEEK_ID="${YEAR}-W${WEEK_NUM}"
OUTPUT_FILE="$ROOT_DIR/data/weekly_reviews/${WEEK_ID}.md"

echo "============================================"
echo "  AI経済圏の創世 — 週次レビュー"
echo "  対象期間: $DATE_FROM 〜 $DATE_TO"
echo "  週ID: $WEEK_ID"
echo "============================================"

mkdir -p "$ROOT_DIR/data/weekly_reviews"

# --- 対象ログ収集 ---
echo "[1/3] 日次ログを収集中..."

LOG_FILES=()
for LOG in "$ROOT_DIR/data/daily_logs/"*.json; do
  [ -f "$LOG" ] || continue
  BASENAME=$(basename "$LOG" .json)
  if [[ "$BASENAME" >= "$DATE_FROM" && "$BASENAME" <= "$DATE_TO" ]]; then
    LOG_FILES+=("$LOG")
  fi
done

if [ ${#LOG_FILES[@]} -eq 0 ]; then
  echo "[警告] 対象期間のログが見つかりません。"
  echo "  期間: $DATE_FROM 〜 $DATE_TO"
  exit 1
fi

echo "  対象ログ数: ${#LOG_FILES[@]} 件"

# --- ログデータ統合 ---
WEEKLY_LOGS=$(python3 - "${LOG_FILES[@]}" <<'PYEOF'
import json, sys
from pathlib import Path

files = sys.argv[1:]
all_data = []
for f in sorted(files):
    try:
        with open(f) as fp:
            all_data.append(json.load(fp))
    except Exception as e:
        print(f"[警告] {f} の読み込み失敗: {e}", file=sys.stderr)

print(json.dumps(all_data, ensure_ascii=False, indent=2))
PYEOF
)

# --- プロンプト組み立て ---
echo "[2/3] 週次レビューを生成中..."

TEMPLATE=$(cat "$ROOT_DIR/prompts/weekly_system_prompt.md")
PROMPT="${TEMPLATE//\{\{WEEKLY_LOGS\}\}/$WEEKLY_LOGS}"
PROMPT="${PROMPT//\{\{YEAR\}\}/$YEAR}"
PROMPT="${PROMPT//\{\{WEEK_NUM\}\}/$WEEK_NUM}"
PROMPT="${PROMPT//\{\{DATE_FROM\}\}/$DATE_FROM}"
PROMPT="${PROMPT//\{\{DATE_TO\}\}/$DATE_TO}"

if ! command -v claude &> /dev/null; then
  echo ""
  echo "[エラー] claude コマンドが見つかりません。"
  echo "Claude Code を開いて「週次レビューを生成して」と伝えてください。"
  exit 1
fi

REVIEW_OUTPUT=$(claude --print -p "$PROMPT" 2>/dev/null)

# --- 保存 ---
echo "$REVIEW_OUTPUT" > "$OUTPUT_FILE"
echo "[3/3] 週次レビュー保存完了"
echo "  ✓ $OUTPUT_FILE"
echo ""
echo "次のステップ："
echo "  1. $OUTPUT_FILE を確認する"
echo "  2. data/context/good_themes.md を更新する"
echo "  3. data/context/bad_themes.md を更新する"
echo "  4. data/context/focus_theme.md に来週の重点テーマを設定する"
echo ""
