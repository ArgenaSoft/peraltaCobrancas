#!/bin/sh

# Encerra se qualquer comando falhar
set -e

# Aplica migrações do banco
echo "Aplicando migrações..."
uv run python manage.py migrate --noinput

# Executa o comando passado ao container (ex: gunicorn)
echo "Inicializando aplicação..."
exec "$@"