class ContentsController < ApplicationController
  def index
    @contents = Content.published
    @contents = @contents.by_category(params[:category]) if params[:category].present?
    @categories = Content::THEME_CATEGORIES
  end

  def show
    @content = Content.published.find(params[:id])
  end
end
