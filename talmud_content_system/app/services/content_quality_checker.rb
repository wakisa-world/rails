# frozen_string_literal: true

class ContentQualityChecker
  Result = Struct.new(:section, :pass, :issues, keyword_init: true) do
    def label
      pass ? "✓" : "✗"
    end
  end

  def initialize(content)
    @content = content
    @config  = BrandConfig.load
  end

  def check
    [
      check_x_post,
      check_free_note,
      check_paid_note,
      check_brand_compliance
    ]
  end

  def passes?
    check.all?(&:pass)
  end

  def summary
    results = check
    {
      overall: results.all?(&:pass),
      results: results,
      issue_count: results.sum { |r| r.issues.length }
    }
  end

  private

  def check_x_post
    issues = []
    len = @content.x_post.to_s.length

    issues << "280文字を超えています（#{len}文字）" if len > 280
    issues << "note導線が含まれていません" unless @content.x_post.to_s.match?(/note/i)
    issues << "クエスチョン形式になっていません" unless @content.x_post.to_s.match?(/[？?]/)

    Result.new(section: "X投稿", pass: issues.empty?, issues: issues)
  end

  def check_free_note
    issues = []
    min = @config.dig(:free_note, :min_length) || 600
    body = @content.free_note_body.to_s

    issues << "本文が短すぎます（#{body.length}文字、最低#{min}文字）" if body.length < min
    issues << "有料noteへの導線がありません" unless body.match?(/有料/)

    Result.new(section: "無料note", pass: issues.empty?, issues: issues)
  end

  def check_paid_note
    issues = []
    min = @config.dig(:paid_note, :min_length) || 1000
    body = @content.paid_note_body.to_s

    issues << "本文が短すぎます（#{body.length}文字、最低#{min}文字）" if body.length < min

    Result.new(section: "有料note", pass: issues.empty?, issues: issues)
  end

  def check_brand_compliance
    issues = []
    all_text = [
      @content.x_post,
      @content.free_note_body,
      @content.paid_note_body
    ].compact.join(" ")

    patterns = @config.dig(:brand, :forbidden_patterns) || []
    patterns.each do |pattern|
      issues << "禁止表現「#{pattern}」が含まれています" if all_text.include?(pattern)
    end

    Result.new(section: "ブランド適合", pass: issues.empty?, issues: issues)
  end
end
