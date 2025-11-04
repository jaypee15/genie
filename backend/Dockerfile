FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright with retry logic and fallback
RUN playwright install chromium || \
    (echo "Playwright install failed, retrying..." && sleep 5 && playwright install chromium) || \
    echo "Playwright installation skipped - will be installed at runtime"

COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh
COPY . .

ENV PYTHONPATH=/app

EXPOSE 8000

ENTRYPOINT ["/app/startup.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

