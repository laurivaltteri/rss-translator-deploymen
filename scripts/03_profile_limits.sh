#!/bin/bash

echo "=== Current Memory Footprint (RSS in KB) ==="
echo "Python Script (if running):"
ps -C python3 -o pid,user,%mem,rss,command || echo "Not running"

echo "Nginx Processes:"
ps -C nginx -o pid,user,%mem,rss,command || echo "Not running"

echo "PostgreSQL Processes (if configured):"
ps -C postgres -o pid,user,%mem,rss,command || echo "Not running"

echo "Miniflux Process (if configured):"
ps -C miniflux -o pid,user,%mem,rss,command || echo "Not running"

echo -e "\n=== Database Storage Size ==="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
if [ -f "$PROJECT_ROOT/db.sqlite3" ]; then
    echo "SQLite Database Size:"
    ls -lh "$PROJECT_ROOT/db.sqlite3" | awk '{print $5}'
fi

if command -v psql &> /dev/null; then
    sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('miniflux')) AS db_size;" 2>/dev/null || echo "Postgres db 'miniflux' not found."
fi

echo -e "\n=== Local Feeds Storage Size ==="
du -sh "$PROJECT_ROOT/feeds/" || echo "Feeds dir not found"
