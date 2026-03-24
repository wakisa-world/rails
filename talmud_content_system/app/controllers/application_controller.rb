class ApplicationController < ActionController::Base
  helper_method :markdown

  private

  def markdown(text)
    return "" if text.blank?
    renderer = Redcarpet::Render::HTML.new(
      hard_wrap: true,
      link_attributes: { target: "_blank", rel: "noopener noreferrer" }
    )
    Redcarpet::Markdown.new(
      renderer,
      autolink: true,
      tables: true,
      fenced_code_blocks: true,
      strikethrough: true,
      no_intra_emphasis: true
    ).render(text).html_safe
  end
end
