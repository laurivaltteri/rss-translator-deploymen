# RSS Translator Pipeline

This project contains a lightweight RSS aggregation and translation pipeline designed to minimize memory usage, specifically targeted for a 1vCPU, 1GB RAM VPS environment.

## Architecture

As per instructions, a pipeline using **Miniflux + PostgreSQL** was initially considered. However, the requirement was to find a **light-weight solution**. Running PostgreSQL and Miniflux natively consumes significant idle RAM (often 100MB+ even when tuned).

To optimize resource usage drastically, this repository implements a pure **Python + SQLite + Nginx** static generation approach:
1. `src/rss_translator.py`: A Python script meant to be run via `cron`. It fetches feeds using `feedparser`, translates them using `deep-translator` (Google Translate by default), and maintains a history of processed items in a local SQLite database `db.sqlite3` to prevent re-translation.
2. It outputs static `.xml` Atom feeds to the `feeds/` directory.
3. `config/nginx_local.conf`: Configures Nginx to serve the static `feeds/` directory directly.

This approach means that **when the translation job isn't running, idle RAM usage is near zero** (only Nginx is running).

### Original Configurations
For completeness and in case the original heavier architecture is still desired, the `miniflux.conf` and `postgresql.conf.patch` files have been retained in the `config/` directory.

## Getting Started

1. Initialize and install dependencies:
   ```bash
   bash scripts/01_install_deps.sh
   ```
2. Setup the environment:
   ```bash
   bash scripts/02_setup_services.sh
   ```
3. Run the translation script:
   ```bash
   cd src
   python rss_translator.py
   ```
4. Check limits and footprint:
   ```bash
   bash scripts/03_profile_limits.sh
   ```
