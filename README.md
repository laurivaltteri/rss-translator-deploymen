# RSS Translator Pipeline

This project contains a lightweight RSS aggregation and translation pipeline designed to minimize memory usage, specifically targeted for a 1vCPU, 1GB RAM VPS environment.

## Architecture

To optimize resource usage drastically, this repository implements a pure **Python + SQLite + Nginx** static generation approach:
1. `src/rss_translator.py`: A Python script meant to be run via `cron`. It fetches feeds using `feedparser`, translates them using `deep-translator` (Google Translate by default), and maintains a history of processed items in a local SQLite database `db.sqlite3` to prevent re-translation.
2. It outputs static `.xml` Atom feeds to the `feeds/` directory.
3. `config/nginx_local.conf`: Configures Nginx to serve the static `feeds/` directory directly.

This approach means that **when the translation job isn't running, idle RAM usage is near zero** (only Nginx is running).

## Getting Started

### 1. Environment Setup & Installation

The project includes setup scripts to install dependencies (Nginx, Python 3, SQLite) and configure the environment:

1. **Install system dependencies**:
   ```bash
   bash scripts/01_install_deps.sh
   ```

2. **Setup virtual environment & services**:
   This will create a Python virtual environment (`.venv`), install required pip packages, create the `feeds/` directory, and link the Nginx configuration.
   ```bash
   bash scripts/02_setup_services.sh
   ```

### 2. Configuration (Adding Feeds)

Before running the translator, configure the RSS feeds you want to aggregate and translate:
1. Open the `feeds_list.txt` file in the root directory.
2. Add the URLs of the RSS feeds you want to follow, one per line. Lines starting with `#` are ignored as comments.

### 3. Usage

To manually trigger the fetching and translation pipeline:
1. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
2. Run the translation script:
   ```bash
   python src/rss_translator.py
   ```

This will output a single `combined.xml` Atom feed into the `feeds/` directory, which is automatically served by Nginx at `http://localhost:8080/combined.xml`. 

*Tip: For automated usage, you can configure a `cron` job to run the included wrapper script at your desired interval (e.g., every 1 hour).*

```bash
# Example: Run every hour
0 * * * * /absolute/path/to/rss-translator-deployment/scripts/run_translator_cron.sh >> /var/log/rss_translator.log 2>&1
```
### 4. Profiling

To check the exact memory footprints of your components and ensure you are staying within the lightweight constraints:
```bash
bash scripts/03_profile_limits.sh
```
