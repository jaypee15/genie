# Genie Cloud Setup Guide

This guide walks you through setting up Genie with Supabase PostgreSQL and Temporal Cloud.

## Prerequisites

- Docker Desktop installed
- OpenAI API account
- Supabase account
- Temporal Cloud account

## Step 1: Supabase Setup

### 1.1 Create Supabase Project

1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Click "New Project"
3. Fill in:
   - Name: `genie-db`
   - Database Password: (generate a strong password)
   - Region: Choose closest to your users
4. Click "Create new project"
5. Wait 2-3 minutes for provisioning

### 1.2 Enable pgvector Extension

1. In your Supabase project, go to **Database** → **Extensions**
2. Search for "vector"
3. Enable the `vector` extension
4. Alternatively, run this SQL in the SQL Editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### 1.3 Get Connection Details

1. Go to **Settings** → **Database**
2. Under "Connection string", select **Connection pooling** → **Transaction** mode
3. Copy the connection string - it looks like:
   ```
   postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-[REGION].pooler.supabase.com:6543/postgres
   ```
4. For Genie, modify it to use `asyncpg`:
   ```
   postgresql+asyncpg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-[REGION].pooler.supabase.com:6543/postgres
   ```

**Important**: Use port **6543** (Transaction mode), not 5432 (Session mode)

### 1.4 Get API Keys

1. Go to **Settings** → **API**
2. Copy:
   - **URL**: Your project URL
   - **anon public**: Public anonymous key
   - **service_role**: Service role secret key

## Step 2: Temporal Cloud Setup

### 2.1 Create Temporal Cloud Account

1. Go to [https://cloud.temporal.io](https://cloud.temporal.io)
2. Sign up for an account
3. Create a new namespace (e.g., `genie-production`)

### 2.2 Get Connection Details

1. From your namespace dashboard, note:
   - **Namespace**: `your-namespace.account-id`
   - **Address**: `your-namespace.tmprl.cloud:7233`

### 2.3 Get API Key

1. In your Temporal Cloud namespace settings
2. Navigate to **API Keys**
3. Click **Create API Key**
4. Copy the generated API key
5. Store it securely - you'll need it for `TEMPORAL_API_KEY`

## Step 3: Configure Environment

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values:

```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...your-anon-key
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...your-service-role-key
DATABASE_URL=postgresql+asyncpg://postgres.xxxxx:your-password@aws-1-us-west-2.pooler.supabase.com:6543/postgres

# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-openai-api-key

# Temporal Cloud Configuration
TEMPORAL_ADDRESS=your-namespace.tmprl.cloud:7233
TEMPORAL_NAMESPACE=your-namespace.account-id
TEMPORAL_API_KEY=your-temporal-api-key

# Application Settings (keep defaults or customize)
APP_NAME=Genie
APP_VERSION=1.0.0
DEBUG=True
SECRET_KEY=generate-a-long-random-string-here
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
SCRAPING_RATE_LIMIT=2
SCRAPING_USER_AGENT=Genie-Bot/1.0
```

## Step 4: Start the Application

1. **Build and start services:**
   ```bash
   docker-compose up -d
   ```

2. **Check logs:**
   ```bash
   # Backend logs (should show successful database connection)
   docker-compose logs -f backend
   
   # Worker logs (should show Temporal connection)
   docker-compose logs -f worker
   ```

3. **Verify database initialization:**
   - Look for log messages:
     - "pgvector extension created/verified"
     - "uuid-ossp extension created/verified"
     - "Database tables created/verified"

4. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Step 5: Verify Setup

### 5.1 Check Database Connection

Visit http://localhost:8000/health/ready

Should return:
```json
{
  "status": "ready",
  "database": "connected"
}
```

### 5.2 Check Temporal Connection

```bash
docker-compose logs worker | grep -i "temporal"
```

Should see: "Temporal worker started"

### 5.3 Create a Test Goal

1. Go to http://localhost:5173
2. Click "Get Started"
3. Click "New Goal"
4. Enter: "Find remote AI engineering jobs"
5. Click "Create Goal"
6. Wait for results (30-60 seconds)

## Troubleshooting

### Database Connection Issues

**Error**: "could not connect to server"

**Solutions**:
1. Verify DATABASE_URL format includes `+asyncpg`
2. Check password is correct (no special characters need escaping)
3. Ensure you're using the **connection pooler** URL, not direct connection
4. Check Supabase project is active (not paused)

**Test connection:**
```bash
# Install psql locally
brew install postgresql  # macOS
# or
sudo apt-get install postgresql-client  # Linux

# Test connection
psql "postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres"
```

### pgvector Extension Issues

**Error**: "type "vector" does not exist"

**Solution**:
```sql
-- Run in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### Temporal Connection Issues

**Error**: "failed to connect to temporal"

**Solutions**:
1. Verify `TEMPORAL_ADDRESS` includes port `:7233`
2. Check `TEMPORAL_NAMESPACE` format: `namespace.account-id`
3. If using mTLS, verify certificates are base64 encoded
4. Check Temporal Cloud namespace is active

**Test with Temporal CLI:**
```bash
# Install Temporal CLI
brew install temporalio/brew/temporal  # macOS
# or follow: https://docs.temporal.io/cli

# Test connection
temporal workflow list \
  --address your-namespace.tmprl.cloud:7233 \
  --namespace your-namespace.account-id
```

### Scraping/crawl4ai Issues

**Error**: "playwright browsers not installed"

**Solution**:
```bash
# Rebuild with clean cache
docker-compose build --no-cache

# Or manually install in container
docker-compose exec backend playwright install chromium
```

### General Debugging

**View all logs:**
```bash
docker-compose logs -f
```

**Restart services:**
```bash
docker-compose restart
```

**Fresh start:**
```bash
docker-compose down
docker-compose up -d
```

## Supabase Tips

### View Data
1. Go to **Table Editor** in Supabase dashboard
2. Browse tables: `users`, `goals`, `opportunities`, `feedback`, `scrape_logs`

### Run Queries
```sql
-- View all goals
SELECT * FROM goals ORDER BY created_at DESC;

-- View opportunities with relevance
SELECT id, title, source_name, opportunity_type, scraped_at 
FROM opportunities 
ORDER BY scraped_at DESC 
LIMIT 20;

-- Check scraping health
SELECT source_name, status, opportunities_found, completed_at 
FROM scrape_logs 
ORDER BY completed_at DESC 
LIMIT 10;
```

### Monitor Performance
- Go to **Database** → **Query Performance**
- Check slow queries
- Add indexes if needed

## Temporal Cloud Tips

### View Workflows
1. Go to your namespace in Temporal Cloud UI
2. Navigate to **Workflows**
3. See running and completed goal processing workflows

### Schedule Daily Scraping
```bash
# Use Temporal CLI or Cloud UI to create a schedule
temporal schedule create \
  --schedule-id daily-scrape \
  --cron "0 2 * * *" \
  --workflow-type DailyScrapeWorkflow \
  --task-queue genie-task-queue
```

### Monitor Workers
- Check **Workers** tab in Temporal Cloud
- Verify worker is connected
- Monitor activity execution

## Security Checklist

- [ ] Change `SECRET_KEY` to a strong random string
- [ ] Store `.env` file securely (never commit to git)
- [ ] Use strong Supabase database password
- [ ] Rotate API keys regularly
- [ ] Enable Row Level Security (RLS) in Supabase for production
- [ ] Use mTLS for Temporal in production
- [ ] Set `DEBUG=False` for production
- [ ] Configure proper CORS origins
- [ ] Set up monitoring and alerts

## Cost Optimization

### Supabase
- **Free tier**: Up to 500 MB database, 2 GB bandwidth
- **Pro tier**: $25/month - Recommended for production
- Monitor usage in dashboard

### Temporal Cloud
- **Free tier**: 1M actions/month
- **Pay as you go**: ~$0.000025 per action
- Monitor in Cloud dashboard

### OpenAI
- **Embeddings**: ~$0.0001 per 1K tokens
- **GPT-4**: ~$0.03 per 1K tokens
- Cache embeddings to reduce costs

## Next Steps

1. **Test thoroughly** with different goal types
2. **Monitor logs** for any errors
3. **Check Supabase usage** in dashboard
4. **Review Temporal workflows** in Cloud UI
5. **Set up scheduled scraping** for continuous updates
6. **Deploy to production** when ready (see DEPLOYMENT.md)

## Support

- **Supabase Docs**: https://supabase.com/docs
- **Temporal Docs**: https://docs.temporal.io
- **Genie Issues**: Check logs and README.md

You're all set! Your Genie instance is now running with cloud infrastructure. 🚀

