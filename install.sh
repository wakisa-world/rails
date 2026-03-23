#!/usr/bin/env bash
# Install script for Ruby on Rails development environment setup.
# Usage: curl -fsSL https://raw.githubusercontent.com/rails/rails/main/install.sh | bash
#    or: bash install.sh

set -e

RUBY_MIN_VERSION="2.7.0"

print_step() {
  echo ""
  echo "==> $1"
}

print_error() {
  echo "ERROR: $1" >&2
}

print_success() {
  echo "✓ $1"
}

version_gte() {
  # Returns 0 (success) if $1 >= $2
  printf '%s\n%s\n' "$2" "$1" | sort -C -V
}

# Detect OS
detect_os() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macos"
  elif [[ -f /etc/debian_version ]]; then
    echo "debian"
  elif [[ -f /etc/redhat-release ]]; then
    echo "redhat"
  else
    echo "unknown"
  fi
}

OS=$(detect_os)

# Check Ruby
print_step "Checking Ruby installation..."
if ! command -v ruby &>/dev/null; then
  print_error "Ruby is not installed."
  echo ""
  echo "Please install Ruby ${RUBY_MIN_VERSION} or newer:"
  echo "  - rbenv: https://github.com/rbenv/rbenv"
  echo "  - RVM:   https://rvm.io"
  echo "  - mise:  https://mise.jdx.dev"
  exit 1
fi

RUBY_VERSION=$(ruby -e "puts RUBY_VERSION")
if ! version_gte "$RUBY_VERSION" "$RUBY_MIN_VERSION"; then
  print_error "Ruby ${RUBY_VERSION} is installed, but Rails requires ${RUBY_MIN_VERSION} or newer."
  exit 1
fi
print_success "Ruby ${RUBY_VERSION}"

# Check Bundler
print_step "Checking Bundler..."
if ! command -v bundle &>/dev/null; then
  echo "Bundler not found. Installing..."
  gem install bundler
fi
print_success "Bundler $(bundle --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')"

# Check Node.js / Yarn
print_step "Checking Node.js and Yarn..."
if ! command -v node &>/dev/null; then
  print_error "Node.js is not installed. Please install Node.js 12+ from https://nodejs.org"
  exit 1
fi
print_success "Node.js $(node --version)"

if ! command -v yarn &>/dev/null; then
  echo "Yarn not found. Installing via npm..."
  npm install -g yarn
fi
print_success "Yarn $(yarn --version)"

# Install system dependencies
print_step "Checking system dependencies..."

if [[ "$OS" == "macos" ]]; then
  if ! command -v brew &>/dev/null; then
    print_error "Homebrew is not installed. Please install it from https://brew.sh"
    exit 1
  fi
  echo "Installing dependencies via Homebrew (this may take a while)..."
  brew bundle --no-upgrade 2>/dev/null || brew bundle
  print_success "System dependencies installed via Homebrew"
elif [[ "$OS" == "debian" ]]; then
  echo "Installing dependencies via apt..."
  sudo apt-get update -qq
  sudo apt-get install -y \
    libmysqlclient-dev \
    libpq-dev \
    libsqlite3-dev \
    libxml2-dev \
    libxslt1-dev \
    libmagickwand-dev \
    ffmpeg \
    imagemagick \
    memcached \
    redis-server \
    2>/dev/null || true
  print_success "System dependencies installed via apt"
else
  echo "Skipping system dependency installation (unsupported OS: $OS)."
  echo "Refer to Brewfile for the list of required dependencies."
fi

# Install Ruby gems
print_step "Installing Ruby gems (bundle install)..."
bundle install
print_success "Ruby gems installed"

# Install JavaScript packages
print_step "Installing JavaScript packages (yarn install)..."
yarn install
print_success "JavaScript packages installed"

echo ""
echo "============================================================"
echo " Rails development environment is ready!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  - Run tests for a component:  cd actionpack && bin/test"
echo "  - Open a console:             tools/console"
echo "  - See CONTRIBUTING.md for more information"
echo ""
