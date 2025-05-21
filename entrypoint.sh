#!/bin/bash

# Espera pelo PostgreSQL
echo "Waiting for PostgreSQL..."
until ping -c 1 db > /dev/null 2>&1; do
  echo "Waiting for db to be available..."
  sleep 2
done

until pg_isready -h db -p 5432 -U postgres > /dev/null 2>&1; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done
echo "PostgreSQL started"

# Executa migrações
python manage.py migrate

# Coleta arquivos estáticos
python manage.py collectstatic --noinput

# Inicia o servidor
gunicorn jota_api.wsgi:application --bind 0.0.0.0:8000