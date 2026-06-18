#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Applying database migrations..."
uv run python manage.py migrate --settings=FactFlow.settings.production --noinput

echo "Starting Gunicorn..."
exec gunicorn FactFlow.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --env DJANGO_SETTINGS_MODULE=FactFlow.settings.production
