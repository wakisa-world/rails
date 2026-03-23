#!/usr/bin/env python3
"""
save_note.py — 日次JSONからnote記事ドラフトMarkdownを生成する

使い方:
  python3 scripts/save_note.py data/daily_logs/2026-03-23.json data/note_drafts/2026-03-23.md
  python3 scripts/save_note.py <json_path> <output_path>
"""
import json
import sys
from pathlib import Path


def generate_note_md(data: dict) -> str:
    date = data.get("date", "記載なし")
    article = data.get("note_article", {})

    if not article:
        return f"# note記事ドラフト — {date}\n\n（note_article データなし。日次実験を再実行してください）\n"

    title = article.get("title", "記載なし")
    target = article.get("target", "記載なし")
    purpose = article.get("purpose", "記載なし")
    body = article.get("body", "記載なし")
    membership_angle = article.get("membership_angle", "記載なし")
    score = article.get("score", 0)
    score_reason = article.get("score_reason", "記載なし")

    md = f"""# {title}

---

## 想定読者
- {target}

## この記事の目的
- {purpose}

---

## 本文

{body}

---

## メンバーシップへの接続
- {membership_angle}

---

## 記事メタ情報
- 実験日：{date}
- スコア：{score} / 100
- スコア理由：{score_reason}
- 状態：ドラフト（要人間レビュー）
"""
    return md


def main():
    if len(sys.argv) < 3:
        print("使い方: python3 save_note.py <json_path> <output_path>")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not json_path.exists():
        print(f"エラー: {json_path} が見つかりません")
        sys.exit(1)

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    md_content = generate_note_md(data)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"生成完了: {output_path}")


if __name__ == "__main__":
    main()
