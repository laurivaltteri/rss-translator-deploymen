#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Setting up Virtual Environment..."
cd "$PROJECT_ROOT"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "Setting up local feeds directory..."
mkdir -p "$PROJECT_ROOT/feeds"

echo "Configuring Nginx..."
# Create a runtime nginx config with the correct absolute path to the local feeds directory
sed "s|/var/www/html/feeds|$PROJECT_ROOT/feeds|g" "$PROJECT_ROOT/config/nginx_local.conf" > "$PROJECT_ROOT/config/nginx_runtime.conf"
sudo ln -sf "$PROJECT_ROOT/config/nginx_runtime.conf" /etc/nginx/sites-enabled/rss_translator.conf
# Ensure nginx user has access
sudo chmod +rx "$PROJECT_ROOT/feeds"
sudo systemctl restart nginx
