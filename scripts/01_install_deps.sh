#!/bin/bash
set -e

# Lightweight installation
echo "Installing dependencies for lightweight RSS translator..."
sudo apt-get update
sudo apt-get install -y nginx python3-venv sqlite3
