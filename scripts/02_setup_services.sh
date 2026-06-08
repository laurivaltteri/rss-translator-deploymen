#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Setting up Virtual Environment..."
cd "$PROJECT_ROOT"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "Setting up /var/www/html/feeds directory..."
sudo mkdir -p /var/www/html/feeds
sudo chown -R $USER:www-data /var/www/html/feeds
sudo chmod -R 775 /var/www/html/feeds

echo "Configuring Nginx..."
sudo ln -sf "$PROJECT_ROOT/config/nginx_local.conf" /etc/nginx/sites-enabled/rss_translator.conf
sudo systemctl restart nginx
