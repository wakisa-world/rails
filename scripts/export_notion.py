#!/usr/bin/env python3
"""
export_notion.py — 日次JSONからNotion貼り付け用Markdownを生成する

使い方:
  python3 scripts/export_notion.py data/daily_logs/2026-03-23.json data/notion_exports/2026-03-23.md
  python3 scripts/export_notion.py <json_path> <output_path>
"""
import json
import sys
from pathlib import Path


def generate_notion_md(data: dict) -> str:
    date = data.get("date", "記載なし")
    hypo = data.get("market_hypothesis", {})
    product = data.get("product_idea", {})
    x_posts = data.get("x_posts", [{}, {}, {}])
    idx = data.get("selected_post_index", 0)
    selected_post = x_posts[idx] if idx < len(x_posts) else {}

    outline_items = product.get("outline", [])
    outline_md = "\n".join(f"  {i+1}. {item}" for i, item in enumerate(outline_items))

    check_points = data.get("operation_note", {}).get("human_check_points", [])
    check_points_md = "\n".join(f"  - {cp}" for cp in check_points)

    def post_section(post: dict, label: str, is_selected: bool = False) -> str:
        star = " ★採用" if is_selected else ""
        return f"""### {label}{star}
- フック：{post.get('hook', '記載なし')}
- 本文：
  {post.get('body', '記載なし').replace(chr(10), chr(10) + '  ')}
- スコア：{post.get('score', 0)} / 100
- 理由：{post.get('score_reason', '記載なし')}"""

    posts_md = ""
    labels = ["案1（思想寄り）", "案2（実験記録寄り）", "案3（学び寄り）"]
    for i, post in enumerate(x_posts[:3]):
        is_selected = (i == idx)
        posts_md += "\n" + post_section(post, labels[i], is_selected) + "\n"

    # note記事セクション
    note = data.get("note_article", {})
    if note:
        note_section = f"""## note記事
- タイトル：{note.get('title', '記載なし')}
- 想定読者：{note.get('target', '記載なし')}
- 目的：{note.get('purpose', '記載なし')}
- メンバーシップ導線：{note.get('membership_angle', '記載なし')}
- スコア：{note.get('score', 0)} / 100
- スコア理由：{note.get('score_reason', '記載なし')}

"""
    else:
        note_section = "## note記事\n（未生成）\n\n"

    # 今日の要点3つ（自動生成）
    key_points = _extract_key_points(data)

    md = f"""# 今日の実験概要
- 日付：{date}
- 今日の市場仮説：{hypo.get('theme', '記載なし')}
- 仮説の理由：{hypo.get('reason', '記載なし')}

---

# 今日AIに作らせたもの

## 商品案
- タイトル：{product.get('title', '記載なし')}
- タイプ：{product.get('type', '記載なし')}
- 誰向けか：{product.get('target', '記載なし')}
- 何が変わるか：{product.get('transformation', '記載なし')}
- 想定価格：{product.get('price_hint', '記載なし')}
- 概要：
{outline_md}
- スコア：{product.get('score', 0)} / 100
- スコア理由：{product.get('score_reason', '記載なし')}

---

## X投稿案
{posts_md}
---

{note_section}---

# 採用したもの
- 採用投稿：{labels[idx] if idx < len(labels) else '記載なし'}
- 採用理由：{data.get('selection_reason', '記載なし')}

---

# 明日への接続
- 明日の改善仮説：{data.get('tomorrow_hypothesis', '記載なし')}
- 人間が確認すべき点：
{check_points_md}
- 再利用アイデア：{data.get('operation_note', {}).get('reuse_idea', '記載なし')}

---

# 今日の要点3つ
- {key_points[0]}
- {key_points[1]}
- {key_points[2]}
"""
    return md


def _extract_key_points(data: dict) -> list:
    """日次データから要点3つを自動抽出する（簡易版）"""
    hypo_theme = data.get("market_hypothesis", {}).get("theme", "")
    product_title = data.get("product_idea", {}).get("title", "")
    tomorrow = data.get("tomorrow_hypothesis", "")

    points = [
        f"今日の仮説：{hypo_theme}" if hypo_theme else "仮説：記載なし",
        f"作ったもの：{product_title}" if product_title else "商品案：記載なし",
        f"明日へ：{tomorrow}" if tomorrow else "明日の仮説：記載なし",
    ]
    return points


def main():
    if len(sys.argv) < 3:
        print("使い方: python3 export_notion.py <json_path> <output_path>")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not json_path.exists():
        print(f"エラー: {json_path} が見つかりません")
        sys.exit(1)

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    md_content = generate_notion_md(data)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"生成完了: {output_path}")


if __name__ == "__main__":
    main()
