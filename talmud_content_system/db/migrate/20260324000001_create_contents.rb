class CreateContents < ActiveRecord::Migration[7.1]
  def change
    create_table :contents do |t|
      t.string  :title,            null: false
      t.string  :source
      t.string  :theme_category,   null: false
      t.text    :x_post,           null: false
      t.string  :free_note_title,  null: false
      t.text    :free_note_body,   null: false
      t.string  :paid_note_title,  null: false
      t.text    :paid_note_body,   null: false
      t.string  :status,           null: false, default: "draft"
      t.datetime :published_at

      t.timestamps
    end

    add_index :contents, :status
    add_index :contents, :theme_category
    add_index :contents, :published_at
  end
end
