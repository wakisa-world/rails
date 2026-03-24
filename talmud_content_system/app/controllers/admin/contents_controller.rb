module Admin
  class ContentsController < ApplicationController
    before_action :set_content, only: [:show, :edit, :update, :destroy, :publish]

    def index
      @contents = Content.order(updated_at: :desc)
    end

    def show
    end

    def new
      @content = Content.new
    end

    def create
      @content = Content.new(content_params)
      if @content.save
        redirect_to admin_content_path(@content), notice: "コンテンツを保存しました。"
      else
        render :new, status: :unprocessable_entity
      end
    end

    def edit
    end

    def update
      if @content.update(content_params)
        redirect_to admin_content_path(@content), notice: "更新しました。"
      else
        render :edit, status: :unprocessable_entity
      end
    end

    def destroy
      @content.destroy
      redirect_to admin_contents_path, notice: "削除しました。"
    end

    def publish
      @content.publish!
      redirect_to admin_content_path(@content), notice: "公開しました。"
    end

    private

    def set_content
      @content = Content.find(params[:id])
    end

    def content_params
      params.require(:content).permit(
        :title,
        :source,
        :theme_category,
        :x_post,
        :free_note_title,
        :free_note_body,
        :paid_note_title,
        :paid_note_body,
        :status
      )
    end
  end
end
