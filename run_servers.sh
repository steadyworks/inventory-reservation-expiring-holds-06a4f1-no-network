#!/bin/bash
set -e

# Ensure pip-installed binaries are on PATH
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"

echo "=== Starting MySQL ==="
mkdir -p /run/mysqld
chown -R mysql:mysql /run/mysqld 2>/dev/null || true

mysqld_safe --datadir=/var/lib/mysql &

# Wait until MySQL is ready (up to 60 seconds)
echo "Waiting for MySQL..."
MYSQL_READY=0
for i in $(seq 1 60); do
  if mysqladmin ping --silent 2>/dev/null; then
    echo "MySQL is ready (after ${i}s)."
    MYSQL_READY=1
    break
  fi
  sleep 1
done

if [ "$MYSQL_READY" -eq 0 ]; then
  echo "ERROR: MySQL did not start in time" >&2
  exit 1
fi

# Create the inventory database
echo "Creating database..."
mysql -u root --password='' -e "CREATE DATABASE IF NOT EXISTS inventory CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null || \
mysql -u root -e "CREATE DATABASE IF NOT EXISTS inventory CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null || true

echo "=== Setting up Django backend ==="
cd /app/backend
pip install -r requirements.txt -q 2>/dev/null || pip install -r requirements.txt

# Run Django migrations to create tables
echo "Running migrations..."
DJANGO_SETTINGS_MODULE=inventory_project.settings python manage.py migrate --noinput

echo "=== Starting Django backend (Daphne on port 3001) ==="
DJANGO_SETTINGS_MODULE=inventory_project.settings \
  daphne -b 0.0.0.0 -p 3001 inventory_project.asgi:application &

echo "=== Setting up React frontend ==="
cd /app/frontend
npm install 2>/dev/null || npm install

echo "=== Starting Vite dev server on port 3000 ==="
npm run build && npx vite preview --port 3000 --host 0.0.0.0 --strictPort &

echo "=== All services started ==="
