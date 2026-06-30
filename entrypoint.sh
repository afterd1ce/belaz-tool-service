#!/bin/sh
echo "Waiting for PostgreSQL..."
until python -c "import psycopg2; psycopg2.connect(host='db', port=5432, user='postgres', password='postgres', dbname='belaz_tools')" 2>/dev/null; do
  echo "Database not ready, waiting..."
  sleep 3
done
echo "PostgreSQL is ready!"
cd /app && python db/init_db.py
echo "Starting API..."
uvicorn main:app --host 0.0.0.0 --port 8000