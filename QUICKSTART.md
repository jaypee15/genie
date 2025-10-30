# Genie - Quick Start Guide

Get Genie running in 5 minutes! ⚡

## Prerequisites

- Docker Desktop installed
- OpenAI API key

## Steps

### 1. Configure Environment (2 minutes)

```bash
# Navigate to project directory
cd genie

# Copy environment template
cp .env .env.local

# Edit the file and add your OpenAI API key
nano .env.local  # or use your favorite editor
```

**Required changes in `.env.local`**:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

### 2. Start Services (2 minutes)

```bash
# Start all services
docker-compose up -d

# Wait for services to be healthy (about 30-60 seconds)
docker-compose ps
```

### 3. Initialize Database (1 minute)

```bash
# Make script executable
chmod +x scripts/init_db.sh

# Run initialization
./scripts/init_db.sh
```

Or manually:
```bash
docker-compose exec db psql -U postgres -d genie -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker-compose exec db psql -U postgres -d genie -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
```

## You're Done! 🎉

### Access Your App

- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Temporal UI**: http://localhost:8080

### Create Your First Goal

1. Open http://localhost:5173
2. Click **"Get Started"**
3. Click **"New Goal"**
4. Enter something like:
   ```
   I want to find remote software engineering jobs 
   focused on AI and machine learning, preferably 
   with compensation above $100k
   ```
5. Click **"Create Goal"**
6. Wait 30-60 seconds for opportunities to appear
7. Browse results and give feedback with 👍/👎

## Troubleshooting

### Services won't start?
```bash
docker-compose logs
```

### Port conflicts?
Edit `docker-compose.yml` to change ports:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Need to restart?
```bash
docker-compose restart
```

### Fresh start?
```bash
docker-compose down -v
docker-compose up -d
./scripts/init_db.sh
```

## What's Next?

- ✅ Check out the [full README](README.md)
- ✅ Read the [setup guide](SETUP.md) for details
- ✅ Review [deployment options](DEPLOYMENT.md)
- ✅ Explore the API at http://localhost:8000/docs

## Common First Goals to Try

**For Jobs**:
```
Find remote Python backend engineer positions at startups
```

**For Speaking**:
```
I want to speak at tech conferences about DevOps and cloud architecture
```

**For Events**:
```
Find virtual tech events and conferences about web development
```

## Need Help?

- Check `docker-compose logs backend` for API errors
- Check `docker-compose logs frontend` for UI errors
- Verify your OpenAI API key is valid
- Ensure all services show "Up" in `docker-compose ps`

---

**Happy opportunity hunting!** 🚀

