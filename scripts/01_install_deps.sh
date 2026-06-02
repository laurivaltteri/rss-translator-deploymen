#!/bin/bash
set -e

# Lightweight installation - avoids Miniflux/Postgres unless explicitly needed
echo "Installing dependencies for lightweight RSS translator..."
sudo apt-get update
sudo apt-get install -y nginx python3-venv sqlite3

# Uncomment below to install Postgres and Miniflux if the heavier architecture is desired
# sudo apt-get install -y postgresql postgresql-contrib
# echo "deb [trusted=yes] https://repo.miniflux.app/apt/ /" | sudo tee /etc/apt/sources.list.d/miniflux.list
# sudo apt-get update
# sudo apt-get install -y miniflux
