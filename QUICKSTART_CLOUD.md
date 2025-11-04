# Genie Cloud - Quick Start Guide

Get Genie running with Supabase and Temporal Cloud in 10 minutes! ⚡

## Prerequisites

- Docker Desktop installed
- OpenAI API key
- Supabase account
- Temporal Cloud account

## Step 1: Set Up Supabase (3 minutes)

1. **Create project** at [app.supabase.com](https://app.supabase.com)
   - Name: `genie-db`
   - Set a strong password
   - Choose your region

2. **Enable pgvector**:
   - Go to **Database** → **Extensions**
   - Enable `vector` extension

3. **Get connection details**:
   - Go to **Settings** → **Database**
   - Copy **Connection pooling** string (Transaction mode)
   - Modify from `postgresql://` to `postgresql+asyncpg://`
   
4. **Get API keys**:
   - Go to **Settings** → **API**
   - Copy URL, anon key, and service_role key

## Step 2: Set Up Temporal Cloud (2 minutes)

1. **Create account** at [cloud.temporal.io](https://cloud.temporal.io)
2. **Create namespace**: e.g., `genie-production`
3. **Note your connection details**:
   - Address: `your-namespace.tmprl.cloud:7233`
   - Namespace: `your-namespace.account-id`

## Step 3: Configure Environment (2 minutes)

1. **Copy environment template**:
   ```bash
   cd genie
   cp .env.example .env
   ```

2. **Edit `.env`** with your values:
   ```bash
   # Supabase
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   DATABASE_URL=postgresql+asyncpg://postgres.xxxxx:password@aws-[REGION].pooler.supabase.com:6543/postgres

   # OpenAI
   OPENAI_API_KEY=sk-your-openai-api-key

   # Temporal Cloud
   TEMPORAL_ADDRESS=your-namespace.tmprl.cloud:7233
   TEMPORAL_NAMESPACE=your-namespace.account-id
   TEMPORAL_API_KEY=your-temporal-api-key

   # Keep these defaults
   APP_NAME=Genie
   DEBUG=True
   SECRET_KEY=change-this-in-production
   ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
   SCRAPING_RATE_LIMIT=2
   ```

## Step 4: Start Application (3 minutes)

1. **Build and start**:
   ```bash
   docker-compose up -d
   ```

2. **Watch startup logs** (wait for "Database initialized successfully"):
   ```bash
   docker-compose logs -f backend
   ```

3. **Verify health**:
   ```bash
   curl http://localhost:8000/health
   ```

## You're Done! 🎉

### Access Your App

- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Create Your First Goal

1. Open http://localhost:5173
2. Click **"Get Started"**
3. Click **"New Goal"**
4. Enter: `Find remote AI/ML engineering jobs with $150k+ salary`
5. Click **"Create Goal"**
6. Wait 30-60 seconds for results
7. Browse and give feedback! 👍/👎

## Verify Everything Works

### Check Database

1. Go to **Table Editor** in Supabase dashboard
2. You should see tables: `users`, `goals`, `opportunities`, `feedback`, `scrape_logs`

### Check Temporal

1. Go to Temporal Cloud dashboard
2. Navigate to your namespace
3. Check **Workers** tab - should show 1 worker connected
4. Check **Workflows** - you'll see workflows when you create goals

### Check Scraping

After creating a goal:
```bash
# Check scrape logs
docker-compose logs worker | grep -i "scraping"

# View opportunities in Supabase
# Go to Table Editor → opportunities table
```

## Troubleshooting

### "Database connection failed"
- Verify DATABASE_URL includes `+asyncpg`
- Check password is correct
- Ensure using **pooler** URL, not direct connection

### "Temporal connection failed"
- Verify TEMPORAL_ADDRESS ends with `:7233`
- Check namespace format: `namespace.account-id`
- Ensure Temporal Cloud namespace is active

### "Playwright browsers not installed"
```bash
docker-compose build --no-cache
docker-compose up -d
```

### View detailed logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f worker
```

### Fresh start
```bash
docker-compose down
docker-compose up -d
```

## What's Next?

✅ Create multiple goals (jobs, speaking, events)  
✅ Provide feedback to improve rankings  
✅ Monitor workflows in Temporal Cloud dashboard  
✅ View data in Supabase Table Editor  
✅ Check CLOUD_SETUP.md for advanced configuration  

## Cost Estimate

**Monthly costs for moderate use:**
- Supabase: Free tier or $25/month (Pro)
- Temporal Cloud: Free tier (~1M actions)
- OpenAI: ~$5-20/month (depending on usage)

**Total**: $0-45/month

## Support

- Full setup guide: `CLOUD_SETUP.md`
- Deployment guide: `DEPLOYMENT.md`  
- Main README: `README.md`

**Happy opportunity hunting with cloud power!** 🚀☁️

