# Genie - AI-Powered Opportunity Discovery Platform

Genie is an intelligent agent that continuously discovers relevant career, speaking, and professional growth opportunities based on your personal goals.

## Features

- **AI-Powered Goal Clarification**: Natural language processing to understand and refine your goals
- **Multi-Source Scraping**: Searches across 8+ platforms including job boards, speaking opportunities, and events
- **Smart Ranking**: Vector similarity search with user feedback integration
- **Continuous Monitoring**: Daily automated scraping for new opportunities
- **Beautiful Dashboard**: Modern React interface with real-time updates

## Architecture

### Backend Stack
- **FastAPI** - High-performance Python web framework
- **PostgreSQL + pgvector** - Database with vector similarity search
- **Temporal** - Workflow orchestration for async tasks
- **OpenAI GPT-4** - LLM for goal clarification and summarization
- **SQLAlchemy** - ORM for database operations
- **Ably** - Managed realtime messaging and WebSocket infrastructure

### Frontend Stack
- **React 18 + TypeScript** - Modern UI framework
- **TanStack Query** - Data fetching and caching
- **Tailwind CSS** - Utility-first styling
- **Vite** - Fast build tool

### Multi-Agent System
1. **Clarifier Agent** - Refines user goals into structured filters
2. **Executor Agent** - Coordinates parallel scraping across sources
3. **Ranker Agent** - Ranks opportunities by relevance with feedback weighting
4. **Coordinator Agent** - Orchestrates the entire workflow

## Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key
- Ably account (for realtime updates)
- Supabase account (for auth and database)
- Temporal Cloud account (for workflow orchestration)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd genie
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. Set up Ably for realtime communication:
See [ABLY_SETUP.md](./ABLY_SETUP.md) for detailed instructions.

4. Start all services:
```bash
docker-compose up -d
```

5. Access the application:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Temporal UI**: http://localhost:8080

### Development Setup

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
genie/
├── backend/
│   ├── app/
│   │   ├── agents/           # Multi-agent system
│   │   ├── api/              # FastAPI routes
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── scrapers/         # Web scrapers
│   │   ├── services/         # Business logic
│   │   ├── workflows/        # Temporal workflows
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database setup
│   │   └── main.py           # FastAPI app
│   ├── alembic/              # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/              # TanStack Query hooks
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── types/            # TypeScript types
│   │   └── App.tsx           # Main app component
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## API Endpoints

### Goals
- `POST /api/goals` - Create a new goal
- `GET /api/goals` - List user's goals
- `GET /api/goals/{id}` - Get goal details
- `PATCH /api/goals/{id}` - Update goal status
- `DELETE /api/goals/{id}` - Delete goal
- `POST /api/goals/{id}/refresh` - Manually trigger scraping

### Opportunities
- `GET /api/opportunities` - List opportunities (with filtering)
- `GET /api/opportunities/{id}` - Get opportunity details

### Feedback
- `POST /api/feedback` - Submit feedback on an opportunity
- `GET /api/feedback` - List user feedback
- `GET /api/feedback/stats` - Get feedback statistics

## Data Sources

Currently integrated sources:
1. **Papercall.io** - Speaking opportunities and CFPs
2. **Sessionize** - Conference speaking slots
3. **RemoteOK** - Remote job listings
4. **We Work Remotely** - Remote jobs
5. **Indeed** - General job search
6. **Y Combinator Jobs** - Startup positions
7. **AngelList (Wellfound)** - Startup jobs
8. **Eventbrite** - Events and conferences

### Adding New Scrapers

1. Create a new scraper in `backend/app/scrapers/`:
```python
from app.scrapers.base import BaseScraper

class NewSourceScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            source_name="newsource",
            base_url="https://newsource.com"
        )
    
    async def scrape(self, filters: dict) -> list:
        # Implement scraping logic
        pass
```

2. Register in `backend/app/scrapers/__init__.py`:
```python
SCRAPER_REGISTRY["newsource"] = NewSourceScraper()
```

## Temporal Workflows

### Goal Processing Workflow
Triggered when a user creates a new goal:
1. Clarify goal with LLM
2. Execute scraping across relevant sources
3. Rank and store opportunities
4. Return results to user

### Daily Scrape Workflow
Runs every 24 hours:
1. Scrape all sources
2. Store new opportunities
3. Log scraping status

### Goal Monitoring Workflow
Continuous monitoring for active goals:
1. Check for new opportunities (every 24h)
2. Rank by relevance
3. Send notifications if new matches found

## Configuration

Key environment variables:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Database (use direct port 5432, not pooled 6543)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

# OpenAI
OPENAI_API_KEY=sk-...

# Temporal Cloud
TEMPORAL_ADDRESS=your-namespace.tmprl.cloud:7233
TEMPORAL_NAMESPACE=your-namespace
TEMPORAL_API_KEY=your-temporal-api-key

# Ably Realtime
ABLY_API_KEY=your-ably-api-key

# Application
SECRET_KEY=your-secret-key-min-32-characters
DEBUG=True
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Scraping
SCRAPING_RATE_LIMIT=2
SCRAPING_USER_AGENT=Genie-Bot/1.0
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### Production Build

1. Build images:
```bash
docker-compose build
```

2. Run in production mode:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Setup
- Set `DEBUG=False` in production
- Use strong `SECRET_KEY`
- Configure proper CORS origins
- Set up SSL/TLS certificates
- Use managed PostgreSQL (recommended)
- Configure monitoring and logging

## Legal & Ethics

- All scrapers respect `robots.txt`
- Rate limiting prevents server overload (1-2 req/sec)
- Only public data is scraped
- Source attribution in all opportunity listings
- No personal data collected without consent

## Roadmap

- [ ] Email notifications
- [ ] Mobile app (React Native)
- [ ] Multi-goal support
- [ ] Advanced filters and preferences
- [ ] Social sharing
- [ ] API partnerships
- [ ] Skills gap analysis
- [ ] Learning resource recommendations

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions:
- GitHub Issues: [repository-url]/issues
- Documentation: [docs-url]

## Acknowledgments

Built with:
- OpenAI GPT-4
- FastAPI
- React
- Temporal
- pgvector
- Tailwind CSS

