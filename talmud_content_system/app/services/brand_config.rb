# frozen_string_literal: true

class BrandConfig
  CONFIG_PATH = Rails.root.join("config", "prompts.yaml")

  class << self
    def load
      @config ||= YAML.safe_load(File.read(CONFIG_PATH)).deep_symbolize_keys
    end

    def reload!
      @config = nil
      load
    end

    def brand
      load[:brand]
    end

    def forbidden_patterns
      load[:brand][:forbidden_patterns] || []
    end

    def x_post
      load[:x_post]
    end

    def free_note
      load[:free_note]
    end

    def paid_note
      load[:paid_note]
    end

    def quality_checks
      load[:quality_check] || []
    end

    def review_criteria
      load[:review][:criteria] || []
    end

    def formatter
      load[:formatter]
    end

    def default_cta
      {
        x: load.dig(:x_post, :required_cta),
        free_note: load.dig(:free_note, :required_cta),
        paid_note: load.dig(:paid_note, :required_cta)
      }
    end

    def prompt_for(role)
      path = Rails.root.join("prompts", "#{role}.md")
      return nil unless path.exist?
      File.read(path)
    end
  end
end
