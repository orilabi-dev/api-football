#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname ${SCRIPT_DIR})"

set -euo pipefail

cd "${PROJECT_ROOT}"

colors_dir="${SCRIPT_DIR}/colors.sh"

source "${colors_dir}"

if [[ ! -f ".env" ]]; then
    error "No environment file present. Run setup.sh and try again."
fi

# Check if API KEY is set
source .env

if [[ -z "${API_SPORTS_KEY:-}" ]]; then
    error "No API Key setup for this repo"
fi

if [[ -z "${DATA_DIR:-}" ]]; then
    data_raw_dir="data/raw"
else
    data_raw_dir="${DATA_DIR}/raw"
fi

if [[ ! -d "${data_raw_dir}" ]]; then
    info "Creating ${data_raw_dir} directory"
    mkdir -p "${data_raw_dir}"
    info "Directory created successfully"

else
    success "Directory already exists"
fi

info "Fetching leagues data"
curl -sf \
    --url "https://v3.football.api-sports.io/leagues" \
    --header "x-apisports-key:${API_SPORTS_KEY}" \
    -o "${data_raw_dir}/leagues.json"

success "Leagues saved to data/leagues.json"