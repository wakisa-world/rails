require_relative "boot"
require "rails/all"

Bundler.require(*Rails.groups)

module TalmudContentSystem
  class Application < Rails::Application
    config.load_defaults 7.1
    config.i18n.default_locale = :ja
    config.time_zone = "Tokyo"
  end
end
