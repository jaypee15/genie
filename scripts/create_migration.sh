#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: ./create_migration.sh <migration_message>"
  exit 1
fi

docker-compose exec backend alembic revision --autogenerate -m "$1"

