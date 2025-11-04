# Genie Setup Guide

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Docker Desktop** (version 20.10 or higher)
   - Download from: https://www.docker.com/products/docker-desktop
   - Ensure Docker Compose is included

2. **OpenAI API Key**
   - Sign up at: https://platform.openai.com
   - Generate an API key from the dashboard

3. **Supabase Account**
   - Sign up at: https://supabase.com
   - Create a new project
   - Get your project URL and API keys

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
git clone <your-repo-url>
cd genie
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env .env.local
```

Edit `.env.local` with your credentials:

```bash
# Required: OpenAI API Key
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Optional: Supabase (or use local PostgreSQL)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Database (default for local development)
DATABASE_URL=postgresql://postgres:password@db:5432/genie
```

### 3. Start Services

Start all services with Docker Compose:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database with pgvector
- Temporal server
- Temporal UI
- Backend API
- Temporal worker
- Frontend application

Wait for all services to be healthy (about 30-60 seconds).

### 4. Initialize Database

Run the initialization script:

```bash
chmod +x scripts/init_db.sh
./scripts/init_db.sh
```

Or manually:

```bash
docker-compose exec db psql -U postgres -d genie -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker-compose exec db psql -U postgres -d genie -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
```

### 5. Verify Installation

Check that all services are running:

```bash
docker-compose ps
```

All services should show "Up" status.

### 6. Access the Application

Open your browser and navigate to:

- **Frontend Application**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Temporal UI**: http://localhost:8080

## First Use

1. **Visit the Landing Page**: http://localhost:5173
2. **Click "Get Started"** to go to the dashboard
3. **Create Your First Goal**:
   - Click "New Goal"
   - Enter something like: "I want to find remote software engineering jobs focused on AI and machine learning"
   - Click "Create Goal"
4. **Wait for Results**: The system will process your goal and search for opportunities (takes 30-60 seconds)
5. **View Opportunities**: Browse the ranked list of opportunities
6. **Provide Feedback**: Click thumbs up/down on opportunities to improve future rankings

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs temporal

# Restart services
docker-compose restart
```

### Database Connection Issues

```bash
# Check if database is healthy
docker-compose ps db

# Restart database
docker-compose restart db

# Wait 10 seconds and try again
sleep 10
```

### Port Conflicts

If ports are already in use, edit `docker-compose.yml` to use different ports:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Change from 8000 to 8001
```

### API Key Issues

Verify your OpenAI API key:

```bash
# Check backend logs for authentication errors
docker-compose logs backend | grep -i "openai\|auth\|api"
```

### Clear Everything and Start Fresh

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: This deletes all data)
docker-compose down -v

# Start fresh
docker-compose up -d

# Re-initialize database
./scripts/init_db.sh
```

## Development Mode

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Running Tests

```bash
# Backend tests
docker-compose exec backend pytest

# Frontend tests
docker-compose exec frontend npm test

# Or use the script
chmod +x scripts/run_tests.sh
./scripts/run_tests.sh
```

## Database Migrations

### Create a New Migration

```bash
chmod +x scripts/create_migration.sh
./scripts/create_migration.sh "add_new_column"
```

### Apply Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### Rollback Migration

```bash
docker-compose exec backend alembic downgrade -1
```

## Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f worker

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Temporal Workflows

Monitor workflows in the Temporal UI:
1. Open http://localhost:8080
2. Navigate to "Workflows"
3. View running and completed workflows

### Database

Connect to the database:

```bash
docker-compose exec db psql -U postgres -d genie
```

## Production Deployment

### Build Production Images

```bash
docker-compose build --no-cache
```

### Environment Variables for Production

Set these in your production environment:

```bash
DEBUG=False
SECRET_KEY=<generate-a-long-random-string>
DATABASE_URL=<your-production-database-url>
ALLOWED_ORIGINS=https://yourdomain.com
```

### Security Checklist

- [ ] Change default database password
- [ ] Generate strong SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure proper CORS origins
- [ ] Use HTTPS/SSL
- [ ] Set up authentication
- [ ] Configure rate limiting
- [ ] Set up monitoring and logging
- [ ] Regular backups of database

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Verify environment variables are set correctly
3. Ensure all services are running: `docker-compose ps`
4. Check the [README.md](README.md) for detailed documentation
5. Open an issue on GitHub with:
   - Error messages from logs
   - Steps to reproduce
   - Your environment (OS, Docker version)

## Next Steps

After successful setup:

1. Explore the API documentation at http://localhost:8000/docs
2. Create multiple goals with different types (speaking, jobs, events)
3. Provide feedback on opportunities to improve rankings
4. Monitor the Temporal UI to see workflows in action
5. Customize scrapers for your specific needs

Enjoy using Genie! 🧞‍♂️

