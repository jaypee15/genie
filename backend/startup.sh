#!/bin/bash
set -e


echo "Running database migrations..."
alembic upgrade head || echo "Migration failed or no migrations to apply"

echo "Starting application..."
exec "$@"

