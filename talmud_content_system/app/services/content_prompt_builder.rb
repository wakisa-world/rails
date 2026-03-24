# frozen_string_literal: true

class ContentPromptBuilder
  ROLES = %w[writer reviewer formatter].freeze

  def initialize(content: nil, theme: nil, source: nil)
    @content = content
    @theme   = theme
    @source  = source
  end

  def writer_prompt
    base = BrandConfig.prompt_for("writer")
    return nil unless base

    inject_theme(base)
  end

  def reviewer_prompt
    base = BrandConfig.prompt_for("reviewer")
    return nil unless base
    return base unless @content

    "#{base}\n\n---\n\n## レビュー対象コンテンツ\n\n#{content_as_text}"
  end

  def formatter_prompt
    base = BrandConfig.prompt_for("formatter")
    return nil unless base
    return base unless @content

    "#{base}\n\n---\n\n## 整形対象コンテンツ\n\n#{content_as_text}"
  end

  private

  def inject_theme(base)
    return base unless @theme || @source

    additions = []
    additions << "**テーマ**: #{@theme}" if @theme
    additions << "**出典**: #{@source}" if @source

    "#{base}\n\n---\n\n## 今回の入力\n\n#{additions.join("\n")}"
  end

  def content_as_text
    return "" unless @content

    <<~TEXT
      ### テーマカテゴリ
      #{@content.theme_category}

      ### X投稿
      #{@content.x_post}

      ### 無料noteタイトル
      #{@content.free_note_title}

      ### 無料note本文
      #{@content.free_note_body}

      ### 有料noteタイトル
      #{@content.paid_note_title}

      ### 有料note本文
      #{@content.paid_note_body}
    TEXT
  end
end
