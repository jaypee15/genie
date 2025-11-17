# Genie - Quick Reference Guide

## 🚀 Common Commands

### Start/Stop Services
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
docker-compose restart worker

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f worker

# Rebuild after code changes
docker-compose up -d --build
```

### Database Operations
```bash
# Connect to database
docker-compose exec db psql -U postgres -d genie

# Run migrations (if needed)
docker-compose exec backend alembic upgrade head

# Check pgvector extension
docker-compose exec db psql -U postgres -d genie -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Debugging
```bash
# Check backend health
curl http://localhost:8000/health

# Check API docs
open http://localhost:8000/docs

# Check frontend
open http://localhost:3000

# Shell into backend container
docker-compose exec backend bash

# Check environment variables
docker-compose exec backend env | grep -E "OPENAI|TEMPORAL|ABLY|SUPABASE"
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required variables
DATABASE_URL=postgresql+asyncpg://...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJxxx...
SUPABASE_JWT_SECRET=your-jwt-secret
OPENAI_API_KEY=sk-xxx
TEMPORAL_ADDRESS=namespace.account.tmprl.cloud:7233
TEMPORAL_NAMESPACE=namespace.account
TEMPORAL_API_KEY=your-temporal-api-key
ABLY_API_KEY=your-ably-api-key
SECRET_KEY=your-secret-key
```

### Frontend Environment (frontend/.env)
```bash
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJxxx...
```

## 📝 API Endpoints

### Chat
- `POST /api/chat/` - Create conversation
- `GET /api/chat/{id}` - Get conversation
- `POST /api/chat/{id}/answer-questions` - Answer clarifying questions
- `GET /api/chat/realtime/token` - Get Ably token

### Goals
- `GET /api/goals/` - List user goals
- `GET /api/goals/{id}` - Get goal details
- `POST /api/goals/` - Create goal (direct, not via chat)
- `PATCH /api/goals/{id}` - Update goal status
- `DELETE /api/goals/{id}` - Delete goal
- `POST /api/goals/{id}/refresh` - Refresh opportunities

### Opportunities
- `GET /api/opportunities/?goal_id={id}` - Get ranked opportunities for goal
- `GET /api/opportunities/{id}` - Get opportunity details

### Feedback
- `POST /api/feedback/` - Submit feedback
- `GET /api/feedback/?goal_id={id}` - Get feedback for goal
- `GET /api/feedback/stats?goal_id={id}` - Get feedback statistics

## 🎯 User Flows

### Create Goal via Chat
1. User visits `/`
2. Types goal description
3. System asks clarifying questions
4. User answers
5. System searches and displays results
6. User clicks to view all opportunities

### View Existing Goals
1. User clicks "Your Goals" in sidebar
2. Dashboard shows all goals
3. Click goal to see opportunities
4. Provide feedback on opportunities

### Manage Goals
1. Go to Dashboard
2. Pause/Resume goal (pause icon)
3. Delete goal (trash icon)
4. Refresh opportunities (refresh button on opportunities page)

## 🐛 Troubleshooting

### Backend not starting
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Missing environment variables
# - Database connection failed
# - Port 8000 already in use

# Fix: Check .env file and restart
docker-compose down
docker-compose up -d
```

### Frontend not connecting to backend
```bash
# Check frontend env
cat frontend/.env

# Should have:
VITE_API_URL=http://localhost:8000

# Restart frontend
docker-compose restart frontend
```

### Ably messages not arriving
```bash
# Check Ably API key
docker-compose exec backend env | grep ABLY_API_KEY

# Check browser console for errors
# Look for "Ably connected" message

# Verify token endpoint
curl -H "Authorization: Bearer YOUR_JWT" http://localhost:8000/api/chat/realtime/token
```

### Scrapers failing
```bash
# Check scraper logs
docker-compose logs backend | grep "Scraper"

# Common issues:
# - Rate limiting
# - Website structure changed
# - Playwright not installed

# Fix: Rebuild backend
docker-compose up -d --build backend
```

### Database connection issues
```bash
# Test connection
docker-compose exec backend python -c "from app.database import engine; print('OK')"

# Check pgvector extension
docker-compose exec db psql -U postgres -d genie -c "\dx"

# Should show "vector" extension
```

### OpenAI API errors
```bash
# Check API key
docker-compose exec backend env | grep OPENAI_API_KEY

# Test API
docker-compose exec backend python -c "from app.services.llm import client; print(client.api_key[:10])"

# Common issues:
# - Invalid API key
# - Rate limit exceeded
# - Model not available
```

## 📊 Monitoring

### Check System Health
```bash
# Backend health
curl http://localhost:8000/health

# Database connections
docker-compose exec db psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Docker stats
docker stats

# Disk usage
docker system df
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Follow errors only
docker-compose logs -f backend 2>&1 | grep -i error
```

## 🔐 Security Checklist

- [ ] `.env` file not committed to git
- [ ] Strong `SECRET_KEY` generated
- [ ] Supabase RLS policies enabled
- [ ] Ably token auth configured
- [ ] CORS origins restricted in production
- [ ] Database password strong
- [ ] API rate limiting enabled
- [ ] HTTPS enabled in production

## 🚀 Deployment Checklist

- [ ] Environment variables set
- [ ] Database migrated
- [ ] pgvector extension installed
- [ ] Supabase project created
- [ ] Temporal Cloud namespace created
- [ ] Ably app created
- [ ] OpenAI API key valid
- [ ] Docker images built
- [ ] Services started
- [ ] Health checks passing
- [ ] Frontend accessible
- [ ] Backend API responding
- [ ] Ably real-time working
- [ ] Authentication working
- [ ] Scrapers running

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Supabase Dashboard**: https://app.supabase.com
- **Temporal Cloud**: https://cloud.temporal.io
- **Ably Dashboard**: https://ably.com/dashboard
- **OpenAI Platform**: https://platform.openai.com

## 💡 Tips

1. **Development**: Use `DEBUG=True` in `.env`
2. **Production**: Set `DEBUG=False` and use HTTPS
3. **Logs**: Always check logs first when debugging
4. **Ably**: Monitor real-time dashboard for connection issues
5. **Scrapers**: Test individually before running full search
6. **Database**: Regular backups recommended
7. **Temporal**: Monitor workflow execution in dashboard
8. **OpenAI**: Watch token usage to avoid rate limits

## 🎓 Learning Resources

- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **crawl4ai**: https://github.com/unclecode/crawl4ai
- **pgvector**: https://github.com/pgvector/pgvector
- **Ably**: https://ably.com/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **React Query**: https://tanstack.com/query/latest

---

**Quick Start**: `docker-compose up -d && open http://localhost:3000`

