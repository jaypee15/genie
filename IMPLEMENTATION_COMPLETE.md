# Genie - AI Opportunity Discovery Platform - Implementation Complete

## Overview

Genie is a fully functional AI-powered opportunity discovery platform that helps users find jobs, speaking engagements, events, and grants through an intelligent multi-agent system.

## ✅ Completed Features

### 1. **Chat-Based Interface**
- ChatGPT-style conversational UI for goal creation
- Real-time status updates during opportunity search
- Conversational clarifying questions (numbered, free-flow)
- Each goal search creates a new chat thread
- Recent chats shown in collapsible sidebar
- Message persistence and history

### 2. **Multi-Agent System (LangGraph)**
- **Clarifier Agent**: Handles all user communication, asks clarifying questions
- **Executor Agent**: Searches across 8+ sources using crawl4ai
- **Ranker Agent**: Uses pgvector for semantic similarity ranking
- **Coordinator Agent**: Orchestrates the entire workflow

### 3. **Web Scraping (crawl4ai + Playwright)**
All scrapers use LLM-powered extraction for resilience:
- ✅ RemoteOK
- ✅ WeWorkRemotely
- ✅ Indeed
- ✅ Papercall.io
- ✅ Sessionize
- ✅ AngelList (Wellfound)
- ✅ Y Combinator Jobs
- ✅ Eventbrite

### 4. **Real-time Communication (Ably)**
- Token-based authentication
- Real-time message delivery
- Status updates during search
- Completion notifications
- Automatic reconnection

### 5. **Authentication (Supabase + Google OAuth)**
- Google sign-in integration
- JWT-based authentication
- Session persistence
- Protected routes
- Automatic user creation on first login

### 6. **Dashboard & Opportunities**
- View all active/paused goals
- Goal management (pause, resume, delete)
- Ranked opportunities with relevance scores
- Feedback system (thumbs up/down)
- Refresh opportunities on demand

### 7. **Database (PostgreSQL + pgvector)**
- Semantic search using embeddings
- Vector similarity for opportunity ranking
- Feedback-based learning
- Efficient indexing

### 8. **Deployment Ready**
- Docker Compose setup
- Environment variable management
- Production-ready configuration
- Temporal Cloud integration for async workflows

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Landing/Chat │  │  Dashboard   │  │ Opportunities│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                    ┌───────▼────────┐                        │
│                    │  Ably Client   │                        │
│                    └───────┬────────┘                        │
└────────────────────────────┼──────────────────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │   Ably Service   │
                    └────────┬─────────┘
                             │
┌────────────────────────────┼──────────────────────────────────┐
│                    Backend (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Chat API    │  │  Goals API   │  │  Opps API    │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                  │                  │               │
│         └──────────────────┴──────────────────┘               │
│                            │                                  │
│                    ┌───────▼────────┐                         │
│                    │  Coordinator   │                         │
│                    │  (LangGraph)   │                         │
│                    └───────┬────────┘                         │
│         ┌──────────────────┼──────────────────┐              │
│         │                  │                  │               │
│  ┌──────▼───────┐  ┌──────▼──────┐  ┌───────▼──────┐        │
│  │  Clarifier   │  │  Executor   │  │   Ranker     │        │
│  │    Agent     │  │    Agent    │  │    Agent     │        │
│  └──────────────┘  └──────┬──────┘  └──────┬───────┘        │
│                            │                │                 │
│                    ┌───────▼────────┐       │                 │
│                    │   8 Scrapers   │       │                 │
│                    │  (crawl4ai)    │       │                 │
│                    └────────────────┘       │                 │
│                                             │                 │
│                    ┌────────────────────────▼──────┐          │
│                    │  PostgreSQL + pgvector        │          │
│                    │  (Supabase)                   │          │
│                    └───────────────────────────────┘          │
└──────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
1. **Supabase Account** (PostgreSQL + pgvector)
2. **Temporal Cloud Account**
3. **OpenAI API Key**
4. **Ably Account**
5. **Docker & Docker Compose**

### Setup

1. **Clone and configure:**
```bash
cd /Users/macintosh/makermode/21-utils/genie
cp .env.example .env
# Edit .env with your credentials
```

2. **Start services:**
```bash
docker-compose up -d
```

3. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📝 Environment Variables

Required in `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJxxx...
SUPABASE_JWT_SECRET=your-jwt-secret

# OpenAI
OPENAI_API_KEY=sk-xxx

# Temporal Cloud
TEMPORAL_ADDRESS=namespace.account.tmprl.cloud:7233
TEMPORAL_NAMESPACE=namespace.account
TEMPORAL_API_KEY=your-temporal-api-key

# Ably
ABLY_API_KEY=your-ably-api-key

# Backend
SECRET_KEY=your-secret-key
DEBUG=True
```

## 🎯 User Flow

1. **User visits landing page** → Sees centered chat interface
2. **User types goal** (e.g., "Find remote AI jobs") → Creates conversation
3. **Clarifier asks questions** → User answers in free-form text
4. **System searches** → Real-time status updates via Ably
5. **Results displayed** → Top 5 opportunities shown in chat with relevance scores
6. **User views all** → Clicks link to see full list on Opportunities page
7. **User provides feedback** → Thumbs up/down on opportunities
8. **System learns** → Future results weighted by feedback

## 🔧 Key Technical Details

### Scrapers (crawl4ai)
- All scrapers use LLM extraction instead of CSS selectors
- Resilient to website structure changes
- Playwright-based for JavaScript-heavy sites
- Rate limiting and robots.txt compliance

### Vector Search (pgvector)
- OpenAI embeddings for goals and opportunities
- Cosine similarity for ranking
- Feedback-weighted scoring
- Efficient indexing for fast queries

### Real-time (Ably)
- Token-based auth with user-specific capabilities
- Separate channels per conversation
- Message, status, and completion events
- Automatic reconnection and message de-duplication

### Authentication (Supabase)
- Google OAuth integration
- JWT verification on backend
- Session persistence in frontend
- Automatic user creation

## 📊 Database Schema

### Core Tables
- `users` - User accounts
- `conversations` - Chat threads
- `messages` - Chat messages
- `goals` - User goals with embeddings
- `opportunities` - Scraped opportunities with embeddings
- `feedback` - User feedback for learning
- `scrape_logs` - Scraping history and errors

## 🐛 Known Issues & Fixes

### Fixed Issues
1. ✅ Pydantic v2 compatibility (`from_orm` → `model_validate`)
2. ✅ Ably publish not awaited (made methods async)
3. ✅ Message duplication (de-duplication by ID)
4. ✅ Messages disappearing (removed invalidateQueries)
5. ✅ Clarifier questions as form (now free-flow text)
6. ✅ Sidebar shifting content (fixed positioning)
7. ✅ Chat input not clickable (WebSocket indicator z-index)

## 📚 Documentation

- `README.md` - Project overview and setup
- `ABLY_SETUP.md` - Ably integration guide
- `AGENT_ARCHITECTURE.md` - Multi-agent system details
- `CLOUD_SETUP.md` - Supabase and Temporal setup
- `DEPLOYMENT.md` - Production deployment guide

## 🎨 UI/UX Features

- Dark theme throughout
- Perplexity-style collapsible sidebar
- Centered chat interface (like ChatGPT)
- Numbered clarifying questions
- Real-time typing indicators
- Relevance score badges
- Smooth animations and transitions

## 🔒 Security

- JWT-based authentication
- Protected API routes
- Supabase Row Level Security (RLS)
- Token-based Ably auth
- Environment variable management
- CORS configuration

## 🚀 Next Steps (Optional Enhancements)

1. **More Sources**: Add LinkedIn, Upwork, Fiverr, etc.
2. **Email Notifications**: Daily digests of new opportunities
3. **Advanced Filters**: Salary range, company size, etc.
4. **Saved Searches**: Save and rerun searches automatically
5. **Team Collaboration**: Share opportunities with team members
6. **Analytics Dashboard**: Track search performance and trends
7. **Mobile App**: React Native version
8. **API Access**: Public API for integrations

## 📞 Support

For issues or questions:
1. Check the documentation files
2. Review Docker logs: `docker-compose logs -f backend`
3. Check Ably dashboard for real-time issues
4. Verify Supabase connection and pgvector extension

---

**Status**: ✅ Production Ready

All core features implemented and tested. The system is ready for deployment and use.

