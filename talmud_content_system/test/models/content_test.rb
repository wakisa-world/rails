require "test_helper"

class ContentTest < ActiveSupport::TestCase
  def valid_attributes
    {
      title: "テストタイトル",
      theme_category: "信用",
      x_post: "テスト投稿文",
      free_note_title: "無料noteタイトル",
      free_note_body: "無料note本文",
      paid_note_title: "有料noteタイトル",
      paid_note_body: "有料note本文"
    }
  end

  test "valid with all required attributes" do
    content = Content.new(valid_attributes)
    assert content.valid?
  end

  test "invalid without title" do
    content = Content.new(valid_attributes.merge(title: ""))
    assert_not content.valid?
    assert_includes content.errors[:title], "can't be blank"
  end

  test "invalid with unknown theme_category" do
    content = Content.new(valid_attributes.merge(theme_category: "存在しないカテゴリ"))
    assert_not content.valid?
  end

  test "invalid when x_post exceeds 280 characters" do
    content = Content.new(valid_attributes.merge(x_post: "a" * 281))
    assert_not content.valid?
    assert content.errors[:x_post].any?
  end

  test "valid x_post at exactly 280 characters" do
    content = Content.new(valid_attributes.merge(x_post: "a" * 280))
    assert content.valid?
  end

  test "defaults to draft status" do
    content = Content.new(valid_attributes)
    assert content.draft?
    assert_not content.published?
  end

  test "publish! sets status to published and records published_at" do
    content = Content.create!(valid_attributes)
    content.publish!
    assert content.published?
    assert_not_nil content.published_at
  end

  test "x_post_length returns character count" do
    content = Content.new(valid_attributes.merge(x_post: "あいう"))
    assert_equal 3, content.x_post_length
  end

  test "published scope returns only published contents" do
    draft   = Content.create!(valid_attributes)
    published = Content.create!(valid_attributes.merge(title: "公開済み", status: "published", published_at: Time.current))
    assert_includes Content.published, published
    assert_not_includes Content.published, draft
  end

  test "by_category scope filters correctly" do
    Content.create!(valid_attributes.merge(theme_category: "信用"))
    Content.create!(valid_attributes.merge(title: "別カテゴリ", theme_category: "契約"))
    assert_equal 1, Content.by_category("契約").count
  end
end
