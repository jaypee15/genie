#!/bin/bash

set -e

echo "Running backend tests..."
docker-compose exec backend pytest

echo "Running frontend tests..."
docker-compose exec frontend npm test

echo "All tests passed!"

