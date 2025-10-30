# Genie Deployment Guide

## Deployment Options

### Option 1: Cloud Platform (Recommended for Production)

#### Deploy to Render.com

1. **Database Setup**:
   - Create a PostgreSQL database on Render
   - Note the connection string
   - Install pgvector extension (contact support if needed)

2. **Backend Deployment**:
   - Create a new Web Service
   - Connect your GitHub repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     ```
     DATABASE_URL=<your-render-postgres-url>
     OPENAI_API_KEY=<your-key>
     TEMPORAL_HOST=<temporal-cloud-url>
     ```

3. **Worker Deployment**:
   - Create a Background Worker
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app/worker.py`
   - Use same environment variables as backend

4. **Frontend Deployment**:
   - Create a Static Site
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`
   - Environment Variables:
     ```
     VITE_API_URL=<your-backend-url>
     ```

#### Deploy to AWS

**Infrastructure Components**:
- **RDS** - PostgreSQL with pgvector
- **ECS/Fargate** - Backend containers
- **S3 + CloudFront** - Frontend hosting
- **Temporal Cloud** or self-hosted on ECS

**Steps**:

1. **Database Setup**:
```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier genie-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15 \
  --master-username postgres \
  --master-user-password <password> \
  --allocated-storage 20
```

2. **ECR Setup**:
```bash
# Create repositories
aws ecr create-repository --repository-name genie-backend
aws ecr create-repository --repository-name genie-worker

# Build and push images
docker build -t genie-backend ./backend
docker tag genie-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/genie-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/genie-backend:latest
```

3. **ECS Task Definitions**:
- Create task definitions for backend and worker
- Configure environment variables
- Set up CloudWatch logs

4. **Frontend to S3**:
```bash
# Build frontend
cd frontend
npm run build

# Upload to S3
aws s3 sync dist/ s3://genie-frontend/

# Configure CloudFront distribution
aws cloudfront create-distribution --origin-domain-name genie-frontend.s3.amazonaws.com
```

### Option 2: DigitalOcean App Platform

1. **Create App**:
   - Connect GitHub repository
   - Add Database component (PostgreSQL)
   - Add Backend service
   - Add Worker service
   - Add Frontend static site

2. **Configure Components**:

Backend:
```yaml
name: backend
dockerfile_path: backend/Dockerfile
envs:
  - key: DATABASE_URL
    scope: RUN_AND_BUILD_TIME
    value: ${db.DATABASE_URL}
  - key: OPENAI_API_KEY
    scope: RUN_AND_BUILD_TIME
    type: SECRET
```

Worker:
```yaml
name: worker
dockerfile_path: backend/Dockerfile
run_command: python app/worker.py
```

Frontend:
```yaml
name: frontend
dockerfile_path: frontend/Dockerfile
envs:
  - key: VITE_API_URL
    value: ${backend.PUBLIC_URL}
```

### Option 3: Self-Hosted VPS

#### Using Docker Compose on VPS

1. **Setup VPS** (Ubuntu 22.04):
```bash
# SSH into VPS
ssh user@your-vps-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin
```

2. **Clone Repository**:
```bash
git clone https://github.com/your-username/genie.git
cd genie
```

3. **Configure Environment**:
```bash
cp .env.example .env
nano .env  # Edit with your values
```

4. **SSL/TLS Setup** (with Let's Encrypt):
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d yourdomain.com
```

5. **Add Nginx Reverse Proxy**:
```nginx
# /etc/nginx/sites-available/genie
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
    }
}
```

6. **Start Services**:
```bash
docker-compose up -d
```

7. **Setup Auto-restart**:
```bash
# Create systemd service
sudo nano /etc/systemd/system/genie.service
```

```ini
[Unit]
Description=Genie Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/user/genie
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable genie
sudo systemctl start genie
```

## Temporal Cloud Setup

For production, use Temporal Cloud instead of self-hosted:

1. **Sign up**: https://temporal.io/cloud
2. **Create Namespace**
3. **Get Connection Info**:
   - Temporal Host URL
   - Namespace
   - Client Certificate

4. **Update Configuration**:
```python
# backend/app/worker.py
from temporalio.client import Client, TLSConfig

client = await Client.connect(
    settings.temporal_host,
    namespace=settings.temporal_namespace,
    tls=TLSConfig(
        client_cert_path="client.pem",
        client_private_key_path="client-key.pem",
    )
)
```

## Monitoring Setup

### Application Monitoring

1. **Sentry** for error tracking:
```bash
pip install sentry-sdk
```

```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
)
```

2. **Prometheus + Grafana**:

Add to docker-compose.yml:
```yaml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  depends_on:
    - prometheus
```

### Database Backups

**Automated Backups**:
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR=/backups
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

docker-compose exec -T db pg_dump -U postgres genie > $BACKUP_DIR/genie_$TIMESTAMP.sql

# Keep only last 30 days
find $BACKUP_DIR -name "genie_*.sql" -mtime +30 -delete
```

**Cron Job**:
```bash
# Run daily at 2 AM
0 2 * * * /home/user/genie/backup.sh
```

## Performance Optimization

### Database

1. **Indexes**:
```sql
CREATE INDEX idx_opportunities_embedding ON opportunities USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_opportunities_type ON opportunities (opportunity_type);
CREATE INDEX idx_opportunities_source ON opportunities (source_name);
CREATE INDEX idx_goals_user ON goals (user_id);
CREATE INDEX idx_goals_status ON goals (status);
```

2. **Connection Pooling**:
```python
# backend/app/database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
)
```

### Caching

Add Redis for caching:
```yaml
# docker-compose.yml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

```python
# backend/app/cache.py
import redis
from functools import wraps

redis_client = redis.Redis(host='redis', port=6379, db=0)

def cache_result(ttl=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### CDN

Use CloudFlare for:
- Static asset caching
- DDoS protection
- Global distribution
- SSL/TLS

## Security Hardening

1. **Environment Variables**:
   - Never commit `.env` files
   - Use secrets management (AWS Secrets Manager, HashiCorp Vault)
   - Rotate API keys regularly

2. **Rate Limiting**:
```python
# backend/app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/goals")
@limiter.limit("100/minute")
async def list_goals():
    ...
```

3. **CORS**:
```python
# Restrict to specific origins
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

4. **Input Validation**:
   - All inputs validated with Pydantic
   - SQL injection prevention with SQLAlchemy
   - XSS prevention in React

5. **Authentication** (Future):
```python
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
```

## Scaling Strategies

### Horizontal Scaling

1. **Backend**: Multiple instances behind load balancer
2. **Worker**: Scale workers based on Temporal queue depth
3. **Database**: Read replicas for queries

### Vertical Scaling

- Increase container resources
- Optimize database queries
- Add indexes

### Cost Optimization

**Development**:
- Use smaller instance types
- Reduce scraping frequency
- Limit OpenAI API calls

**Production**:
- Reserved instances for predictable workloads
- Auto-scaling based on metrics
- Cache embeddings aggressively

## Health Checks

```python
# backend/app/main.py
@app.get("/health/live")
async def liveness():
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute("SELECT 1")
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable")
```

## Troubleshooting Production Issues

### High Database Load
- Check slow query log
- Add missing indexes
- Implement query caching

### Memory Issues
- Monitor container memory usage
- Check for memory leaks
- Optimize scraper batch sizes

### API Timeouts
- Increase timeout settings
- Optimize slow endpoints
- Add request queuing

### Scraping Failures
- Check robots.txt compliance
- Verify rate limiting
- Monitor IP blocks
- Rotate user agents

## Rollback Procedure

```bash
# Tag current version
git tag -a v1.0.0 -m "Release 1.0.0"

# If issues occur, rollback:
git checkout v1.0.0
docker-compose down
docker-compose build
docker-compose up -d
```

## Maintenance Windows

Schedule for:
- Database migrations
- Major version upgrades
- Index rebuilding
- Backup verification

**Communication**:
- Notify users 48 hours in advance
- Status page for real-time updates
- Post-mortem for incidents

## Support Resources

- Temporal Docs: https://docs.temporal.io
- FastAPI Docs: https://fastapi.tiangolo.com
- pgvector Guide: https://github.com/pgvector/pgvector
- React Query Docs: https://tanstack.com/query

## Emergency Contacts

Maintain a runbook with:
- Service URLs and credentials
- Database access procedures
- Backup restoration steps
- Monitoring dashboard links
- On-call rotation schedule

