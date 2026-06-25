#!/bin/sh
echo "Ждём запуск PostgreSQL..."
until python -c "import psycopg2; psycopg2.connect(host='db', port=5432, user='postgres', password='postgres', dbname='belaz_tools')" 2>/dev/null; do
  echo "База данных ещё не готова, ждём..."
  sleep 3
done
echo "PostgreSQL готов!"
python init_db.py
echo "Запускаем API..."
uvicorn main:app --host 0.0.0.0 --port 8000