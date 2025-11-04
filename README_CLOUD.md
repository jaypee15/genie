# Genie - Cloud-Native Setup 🌩️

This version of Genie uses cloud services for production-ready deployment:

- **Supabase**: PostgreSQL database with pgvector
- **Temporal Cloud**: Workflow orchestration
- **crawl4ai**: Advanced web scraping with Playwright

## Key Differences from Local Setup

| Component | Local Version | Cloud Version |
|-----------|---------------|---------------|
| Database | Docker PostgreSQL | Supabase (managed) |
| Workflows | Docker Temporal | Temporal Cloud |
| Scraping | Basic | crawl4ai + Playwright |
| Initialization | Manual scripts | Automatic on startup |
| Scaling | Single machine | Cloud-native |

## Quick Start

```bash
# 1. Set up cloud accounts (one-time)
# - Create Supabase project
# - Create Temporal Cloud namespace
# - Get OpenAI API key

# 2. Configure
cp .env.example .env
# Edit .env with your credentials

# 3. Start
docker-compose up -d

# 4. Use
open http://localhost:5173
```

## Files Updated for Cloud

### Removed
- ❌ Local PostgreSQL container
- ❌ Local Temporal server
- ❌ Local Temporal UI
- ❌ Manual initialization scripts
- ❌ `postgres_data` volume

### Updated
- ✅ `docker-compose.yml` - Simplified to 3 services only
- ✅ `backend/app/database.py` - Idempotent initialization
- ✅ `backend/app/worker.py` - Temporal Cloud connection with TLS
- ✅ `backend/app/scrapers/` - Now using crawl4ai
- ✅ `backend/Dockerfile` - Includes Playwright setup
- ✅ `.env.example` - Cloud configuration template

### Added
- ✅ `CLOUD_SETUP.md` - Detailed cloud setup guide
- ✅ `QUICKSTART_CLOUD.md` - 10-minute quick start
- ✅ `backend/startup.sh` - Automatic initialization
- ✅ `backend/app/scrapers/crawl4ai_base.py` - crawl4ai integration

## Architecture

```
┌─────────────┐
│   Frontend  │ (Docker)
│   React     │
└──────┬──────┘
       │
       ▼
┌─────────────┐       ┌──────────────┐
│   Backend   │◄─────►│   Supabase   │
│   FastAPI   │       │  PostgreSQL  │
└──────┬──────┘       │  + pgvector  │
       │              └──────────────┘
       ▼
┌─────────────┐       ┌──────────────┐
│   Worker    │◄─────►│Temporal Cloud│
│   Temporal  │       │  Workflows   │
└─────────────┘       └──────────────┘
       │
       ▼
┌─────────────┐
│  crawl4ai   │
│  Playwright │
│  Scrapers   │
└─────────────┘
```

## Benefits of Cloud Setup

### Reliability
- ✅ Managed database with automatic backups
- ✅ High availability workflows
- ✅ No local infrastructure maintenance

### Scalability
- ✅ Database scales with your data
- ✅ Workers can scale horizontally
- ✅ Global edge deployments possible

### Features
- ✅ pgvector extension already enabled
- ✅ Temporal Cloud monitoring and debugging
- ✅ Advanced scraping with JavaScript rendering

### Developer Experience
- ✅ No manual initialization needed
- ✅ Automatic database migrations
- ✅ Easy to deploy anywhere

## Environment Variables

### Required
```bash
# Supabase (from your Supabase project)
# Use Transaction pooler: port 6543
DATABASE_URL=postgresql+asyncpg://postgres.xxxxx:password@aws-1-region.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON__KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# OpenAI (from platform.openai.com)
OPENAI_API_KEY=sk-...

# Temporal Cloud (from cloud.temporal.io)
TEMPORAL_ADDRESS=namespace.tmprl.cloud:7233
TEMPORAL_NAMESPACE=namespace.account-id
TEMPORAL_API_KEY=your-temporal-api-key
```

### Optional
```bash

# Application settings
DEBUG=True
SECRET_KEY=change-in-production
ALLOWED_ORIGINS=http://localhost:5173
```

## Docker Services

### 1. Backend (FastAPI)
- Serves REST API
- Auto-initializes database
- Health checks

### 2. Worker (Temporal)
- Executes workflows
- Connects to Temporal Cloud
- Runs scrapers

### 3. Frontend (React)
- User interface
- Development server
- Proxies API requests

## Initialization Process

When backend starts:

1. **Connect to Supabase**
   ```
   ✅ Database connection established
   ```

2. **Enable extensions** (idempotent)
   ```
   ✅ pgvector extension created/verified
   ✅ uuid-ossp extension created/verified
   ```

3. **Create tables** (idempotent)
   ```
   ✅ Database tables created/verified
   ```

4. **Ready for requests**
   ```
   ✅ Application startup complete
   ```

All operations are idempotent - safe to run multiple times.

## Scraping with crawl4ai

### Features
- 🌐 JavaScript rendering with Playwright
- 📄 Markdown extraction
- ⚡ Async operation
- 🔄 Automatic retries
- 🤖 Robots.txt compliance

### Example Scraper

```python
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper

class MyScraper(Crawl4AIBaseScraper):
    def __init__(self):
        super().__init__("mysource", "https://example.com")
    
    async def scrape(self, filters):
        html = await self._crawl("/opportunities")
        # Parse and return opportunities
```

## Monitoring

### Supabase Dashboard
- **Table Editor**: View data
- **SQL Editor**: Run queries
- **Database**: Monitor performance
- **Logs**: Track errors

### Temporal Cloud Dashboard
- **Workflows**: View executions
- **Workers**: Check connectivity
- **Schedules**: Manage cron jobs
- **Metrics**: Monitor performance

### Application Logs
```bash
# View all logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Worker only
docker-compose logs -f worker
```

## Common Tasks

### View Database Data
```sql
-- In Supabase SQL Editor
SELECT * FROM goals ORDER BY created_at DESC LIMIT 10;
SELECT * FROM opportunities ORDER BY scraped_at DESC LIMIT 20;
SELECT * FROM scrape_logs ORDER BY completed_at DESC LIMIT 10;
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart worker
```

### Update Code
```bash
# Pull changes
git pull

# Rebuild
docker-compose build

# Restart
docker-compose up -d
```

### View Workflows
1. Go to Temporal Cloud dashboard
2. Select your namespace
3. Navigate to "Workflows"
4. See real-time execution

## Troubleshooting

### Database Issues

**Symptom**: "could not connect to server"

**Check**:
1. Verify DATABASE_URL format includes `+asyncpg`
2. Ensure Supabase project is active
3. Check password is correct
4. Use pooler URL, not direct connection

**Test connection**:
```bash
# Install psql
brew install postgresql

# Test
psql "your-database-url"
```

### Temporal Issues

**Symptom**: "failed to connect to temporal"

**Check**:
1. Verify TEMPORAL_ADDRESS ends with `:7233`
2. Check TEMPORAL_NAMESPACE format
3. Ensure namespace is active in dashboard

**Test connection**:
```bash
# Install Temporal CLI
brew install temporalio/brew/temporal

# Test
temporal workflow list \
  --address your-namespace.tmprl.cloud:7233 \
  --namespace your-namespace.account-id
```

### Scraping Issues

**Symptom**: "playwright browsers not installed"

**Solution**:
```bash
# Rebuild with clean cache
docker-compose build --no-cache

# Restart
docker-compose up -d
```

## Security Checklist

Before production:

- [ ] Change SECRET_KEY to strong random value
- [ ] Set DEBUG=False
- [ ] Use strong database password
- [ ] Rotate API keys regularly
- [ ] Configure proper CORS origins
- [ ] Enable Supabase Row Level Security
- [ ] Use mTLS for Temporal in production
- [ ] Set up monitoring alerts
- [ ] Configure rate limiting
- [ ] Review and harden scrapers

## Cost Optimization

### Supabase
- Start with free tier (500MB database)
- Upgrade to Pro ($25/month) when needed
- Monitor database size
- Clean old data periodically

### Temporal Cloud
- Free tier: 1M actions/month
- Monitor action count
- Optimize workflow execution
- Use efficient activities

### OpenAI
- Cache embeddings aggressively
- Use GPT-4o-mini for summaries
- Batch requests when possible
- Monitor token usage

## Documentation

- **CLOUD_SETUP.md**: Detailed setup instructions
- **QUICKSTART_CLOUD.md**: 10-minute quick start
- **DEPLOYMENT.md**: Production deployment
- **README.md**: Original comprehensive guide

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify environment variables
3. Test cloud service connectivity
4. Review cloud dashboards
5. Check documentation

## Advantages Over Local Setup

| Aspect | Benefit |
|--------|---------|
| **Setup Time** | 10 min vs 30+ min |
| **Maintenance** | Zero vs ongoing |
| **Reliability** | 99.9% vs depends |
| **Scalability** | Unlimited vs limited |
| **Monitoring** | Built-in dashboards |
| **Backups** | Automatic vs manual |
| **Updates** | Managed vs DIY |

---

**Ready to scale? This cloud setup is production-ready!** 🚀

