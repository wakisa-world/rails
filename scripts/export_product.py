#!/usr/bin/env python3
"""
export_product.py — 日次JSONから商品案ストック用Markdownを生成する

使い方:
  python3 scripts/export_product.py data/daily_logs/2026-03-23.json data/product_ideas/2026-03-23.md
  python3 scripts/export_product.py <json_path> <output_path>
"""
import json
import sys
from pathlib import Path


def generate_product_md(data: dict) -> str:
    date = data.get("date", "記載なし")
    product = data.get("product_idea", {})
    x_posts = data.get("x_posts", [])
    idx = data.get("selected_post_index", 0)
    selected_post = x_posts[idx] if idx < len(x_posts) else {}

    outline_items = product.get("outline", [])
    outline_md = "\n".join(f"  {i+1}. {item}" for i, item in enumerate(outline_items))

    # 商品化優先度をスコアから自動判定
    score = product.get("score", 0)
    if score >= 85:
        priority = "高"
    elif score >= 70:
        priority = "中"
    else:
        priority = "低"

    # 採用投稿のhookを再利用元として記録
    reuse_hook = selected_post.get("hook", "記載なし")

    md = f"""# 商品案ストック — {date}

- 商品名：{product.get('title', '記載なし')}
- 商品タイプ：{product.get('type', '記載なし')}
- 誰向けか：{product.get('target', '記載なし')}
- 何が変わるか：{product.get('transformation', '記載なし')}
- 元になった実験日：{date}
- 想定価格：{product.get('price_hint', '記載なし')}
- 目次・構成：
{outline_md}
- 商品化優先度：{priority}（スコア {score}/100 より自動判定）
- 状態：構想中
- 再利用元投稿：{reuse_hook}
- 備考：{product.get('score_reason', '記載なし')}
"""
    return md


def main():
    if len(sys.argv) < 3:
        print("使い方: python3 export_product.py <json_path> <output_path>")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not json_path.exists():
        print(f"エラー: {json_path} が見つかりません")
        sys.exit(1)

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    md_content = generate_product_md(data)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"生成完了: {output_path}")


if __name__ == "__main__":
    main()


