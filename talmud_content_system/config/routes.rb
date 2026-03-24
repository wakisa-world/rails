Rails.application.routes.draw do
  root "contents#index"

  resources :contents, only: [:index, :show]

  namespace :admin do
    root "contents#index"
    resources :contents do
      member do
        patch :publish
      end
    end
  end
end
