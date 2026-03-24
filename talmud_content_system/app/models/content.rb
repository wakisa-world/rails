class Content < ApplicationRecord
  THEME_CATEGORIES = %w[
    信用
    契約
    判断
    欲望
    自制
    長期視点
    問いを立てる力
  ].freeze

  STATUSES = %w[draft published].freeze

  validates :title,           presence: true
  validates :theme_category,  presence: true, inclusion: { in: THEME_CATEGORIES }
  validates :x_post,          presence: true, length: { maximum: 280 }
  validates :free_note_title, presence: true
  validates :free_note_body,  presence: true
  validates :paid_note_title, presence: true
  validates :paid_note_body,  presence: true
  validates :status,          inclusion: { in: STATUSES }

  scope :published, -> { where(status: "published").order(published_at: :desc) }
  scope :drafts,    -> { where(status: "draft").order(updated_at: :desc) }
  scope :by_category, ->(cat) { where(theme_category: cat) }

  def published?
    status == "published"
  end

  def draft?
    status == "draft"
  end

  def publish!
    update!(status: "published", published_at: Time.current)
  end

  def x_post_length
    x_post.to_s.length
  end
end
