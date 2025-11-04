#!/bin/bash
set -e

echo "Installing Playwright browsers..."
playwright install chromium

echo "Starting application..."
exec "$@"

