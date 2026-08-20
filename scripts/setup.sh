#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname ${SCRIPT_DIR})"

cd "${PROJECT_ROOT}"

colors_dir="${SCRIPT_DIR}/colors.sh"

source "${colors_dir}"

set -euo pipefail

info "Setting up your repo..."

# Check python3 is available
if ! command -v python3 &> /dev/null; then
    error "Python 3 is not installed or not on your PATH"
fi

success "Python 3 found: $(python3 --version)"

# Check uv is available
if ! command -v uv &> /dev/null; then
    error "uv is not installed or not on your PATH. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

success "uv found: $(uv --version)"

# Initialize uv
if [[ ! -f "pyproject.toml" ]]; then
    info "uv is not yet initialized in this directory. Initializing now..."
    uv init
    rm "main.py"
    info "uv initialized successfully."
else
    info "uv already initialized"
fi

# Initialize .env
if [[ ! -f ".env" ]]; then
    info ".env not found — copying from .env.example..."
    cp .env.example .env
    success ".env created. Open it and fill in your API keys before running anything"
else
    info ".env already exists"
fi

# Setup virtual environment
if [[ ! -d ".venv" ]]; then
    info "Virtual environment not yet setup for this project"
    uv sync
else
    info "Virtual environment initialized"
fi

info ""
success "Setup complete. To activate your environment run:"
success "  source .venv/bin/activate"