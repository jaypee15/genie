#!/bin/bash

set -e

echo "Waiting for database to be ready..."
sleep 5

echo "Creating database extensions..."
docker-compose exec db psql -U postgres -d genie -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker-compose exec db psql -U postgres -d genie -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

echo "Running migrations..."
docker-compose exec backend alembic upgrade head

echo "Database initialization complete!"

