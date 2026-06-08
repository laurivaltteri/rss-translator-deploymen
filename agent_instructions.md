# Setup instructions for a feed service

## 1. Context & Objective
Initialize a local Git repository for developing and testing a native, non-containerized RSS aggregator and translation pipeline. The objective is to simulate a production VPS environment (Debian/Ubuntu, 1 vCPU, 1 GB RAM, 10 GB SSD) within a local WSL2 environment, monitor the exact memory and storage limits of the native components (Miniflux, PostgreSQL, Nginx, Python script), and prepare the configuration for remote deployment.

## 2. Workspace Initialization
1.  You are in initialized Git repository in the current workspace.
2.  Create a standard `.gitignore` tailored for Python and VS Code:
    ```text
    __pycache__/
    *.pyc
    .venv/
    .env
    .vscode/
    feeds/
    ```
4.  Create the following project structure:
    ```text
    rss-translator-deployment/
    ├── src/
    │   └── rss_translator.py     # The Python ETL script
    ├── config/
    │   ├── miniflux.conf         # Miniflux configuration
    │   ├── nginx_local.conf      # Nginx server block
    │   └── postgresql.conf.patch # DB memory constraints
    ├── scripts/
    │   ├── 01_install_deps.sh    # Script to install native packages
    │   ├── 02_setup_services.sh  # Script to configure Nginx/Postgres/Miniflux
    │   └── 03_profile_limits.sh  # Script to monitor RAM/Disk usage
    ├── requirements.txt          # Python dependencies
    └── README.md
    ```

## 3. File Generation Tasks

### Task 3.1: Python Dependencies & Script
1.  Generate `requirements.txt`:
    ```text
    feedparser==6.0.11
    feedgen==1.0.0
    httpx==0.27.0
    ```
2.  Populate `src/rss_translator.py` with the translation script logic specified in the previous architecture document. Ensure paths point to a local relative directory (e.g., `../feeds/`) for testing purposes instead of `/var/www/html/feeds/`.

### Task 3.2: Service Configurations
1.  Populate `config/miniflux.conf` with the aggressive pruning parameters:
    ```ini
    LISTEN_ADDR=127.0.0.1:8080
    DATABASE_URL=postgres://miniflux:localtest@localhost:5432/miniflux?sslmode=disable
    RUN_MIGRATIONS=1
    CREATE_ADMIN=1
    ADMIN_USERNAME=admin
    ADMIN_PASSWORD=localtest
    CLEANUP_ARCHIVE_READ_DAYS=7
    CLEANUP_ARCHIVE_UNREAD_DAYS=14
    CLEANUP_ARCHIVE_BATCH_SIZE=100
    ```
2.  Populate `config/postgresql.conf.patch` with the memory constraints specifically targeted for the 1GB RAM limit:
    ```ini
    max_connections = 20
    shared_buffers = 32MB
    effective_cache_size = 128MB
    maintenance_work_mem = 16MB
    work_mem = 2MB
    huge_pages = off
    autovacuum = on
    autovacuum_max_workers = 3
    autovacuum_naptime = 1min
    autovacuum_vacuum_threshold = 50
    autovacuum_vacuum_scale_factor = 0.2
    ```

### Task 3.3: Deployment & Profiling Scripts
1.  Generate `scripts/01_install_deps.sh` to install PostgreSQL, Nginx, and Miniflux locally via apt.
2.  Generate `scripts/02_setup_services.sh` to:
    * Create the local `feeds` directory.
    * Apply the `postgresql.conf.patch` to the local Postgres installation.
    * Initialize the Miniflux database and user.
    * Symlink `config/nginx_local.conf` to Nginx and `config/miniflux.conf` to `/etc/miniflux.conf`.
3.  Generate `scripts/03_profile_limits.sh` to monitor and output the resource footprint. This is critical for validating the 1GB RAM constraint.
    ```bash
    #!/bin/bash
    echo "=== Current Memory Footprint (RSS in KB) ==="
    echo "PostgreSQL Processes:"
    ps -C postgres -o pid,user,%mem,rss,command
    echo "Miniflux Process:"
    ps -C miniflux -o pid,user,%mem,rss,command
    echo "Nginx Processes:"
    ps -C nginx -o pid,user,%mem,rss,command
    
    echo -e "\n=== Database Storage Size ==="
    sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('miniflux')) AS db_size;"
    
    echo -e "\n=== Local Feeds Storage Size ==="
    du -sh ../feeds/
    ```

## 4. Execution Directives
After generating all files, commit the initial state to the Git repository. Do not execute the bash scripts automatically; simply prepare the workspace so the user can review the code in VS Code, run the local deployment scripts manually, and execute `scripts/03_profile_limits.sh` to verify constraints before pushing to the VPS.
