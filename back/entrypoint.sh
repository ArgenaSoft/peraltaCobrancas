#!/bin/sh
set -e

echo "Aplicando migrações..."
python manage.py migrate --noinput

echo "Inicializando aplicação..."
exec "$@"