# Ably Setup Guide

This guide explains how to set up Ably for realtime communication in the Genie application.

## Overview

Genie uses Ably for scalable, reliable realtime updates between the backend and frontend. This replaces the previous WebSocket implementation with a managed service that provides:

- Automatic reconnection and message delivery
- Presence and typing indicators support
- Message history and rewind on reconnect
- Global CDN and low-latency message delivery
- Built-in rate limiting and backpressure

## Setup Steps

### 1. Create Ably Account

1. Go to [https://ably.com/signup](https://ably.com/signup)
2. Sign up for a free account
3. Verify your email address

### 2. Create a New App

1. Log into the Ably dashboard
2. Click "Create New App"
3. Give it a name (e.g., "Genie")
4. Click "Create App"

### 3. Get Your API Key

1. In your app dashboard, go to the "API Keys" tab
2. Copy the **Root** API key
   - It looks like: `xVLyHw.xxxxxx:xxxxxxxxxx`
   - The first part (before the dot) is your App ID
   - The full string is your API key

### 4. Configure Backend

Add the API key to your backend environment:

```bash
# backend/.env
ABLY_API_KEY=your_ably_api_key_here
```

### 5. Restart Services

```bash
# Restart backend and worker to pick up the new environment variable
docker-compose restart backend worker

# Or rebuild if you've made code changes
docker-compose up -d --build backend worker
```

### 6. Install Frontend Dependencies

```bash
cd frontend
npm install
```

This will install the `ably` package that was added to `package.json`.

## Monitoring and Debugging

### Ably Dashboard

Monitor your realtime activity:

- **Stats**: [https://ably.com/accounts/[your-account]/apps/[your-app]/stats](https://ably.com/accounts)
- **Dev Console**: [https://ably.com/accounts/[your-account]/apps/[your-app]/dev-console](https://ably.com/accounts)
- **Channel Inspector**: View active channels and messages in realtime

### Free Tier Limits

The free tier includes:

- 200 peak connections
- 6 million messages per month
- 50 GB data transfer
- 24-hour message history

This is sufficient for development and small-scale production use.

### Browser Console

Check the browser console for Ably connection status:

```
Ably connected  // Successful connection
Ably connection error: ...  // Connection issues
```

### Backend Logs

Check backend logs for Ably publishing activity:

```bash
docker-compose logs -f backend | grep Ably
```

You should see:
```
Published message to conversation:xxx
Published status to conversation:xxx - searching
Published completion to conversation:xxx
```

## Channel Architecture

Genie uses a simple channel structure:

- **Channel Pattern**: `conversation:{conversation_id}`
- **Message Types**:
  - `message`: New assistant messages
  - `status`: Progress updates (searching, processing, complete, error)
  - `complete`: Final completion event with goal_id and opportunities count

### Example Channel

For conversation ID `abc-123-def-456`:
- Channel: `conversation:abc-123-def-456`
- Only the authenticated user who owns this conversation can subscribe
- Only the backend can publish to this channel

## Security

### Token-Based Authentication

Genie uses Ably's token authentication for security:

1. Frontend requests a token from backend endpoint: `GET /api/chat/realtime/token`
2. Backend verifies user authentication (Supabase JWT)
3. Backend generates Ably token with restricted capabilities:
   - **Capability**: `conversation:*` with `subscribe` only
   - **Client ID**: User's UUID
   - **TTL**: 1 hour
4. Frontend uses this token to connect to Ably
5. Token expires after 1 hour, triggering automatic re-authentication

### Channel Security

- Users can **only subscribe** to channels (no publish)
- Users can subscribe to any `conversation:*` channel
- Backend verifies conversation ownership before sending messages
- Only backend (with full API key) can publish messages

## Troubleshooting

### "Ably connection error" in Browser

**Check**:
1. Is backend running and accessible?
2. Is user authenticated (logged in)?
3. Check network tab for `/api/chat/realtime/token` request
4. Check browser console for detailed error message

**Solutions**:
- Ensure `ABLY_API_KEY` is set in backend `.env`
- Restart backend after adding the key
- Clear browser cache and reload

### "Error publishing message to Ably" in Backend Logs

**Check**:
1. Is `ABLY_API_KEY` correct?
2. Is the API key active (not revoked)?
3. Have you exceeded free tier limits?

**Solutions**:
- Verify API key in Ably dashboard
- Check Ably dashboard for error messages
- Upgrade to paid tier if needed

### Messages Not Appearing in Frontend

**Check**:
1. Is Ably connected? (check browser console)
2. Are messages being published? (check backend logs)
3. Is conversation_id correct?

**Solutions**:
- Check browser console for subscription errors
- Verify `conversation_id` matches between frontend and backend
- Check Dev Console in Ably dashboard for channel activity

### Rate Limiting

If you hit rate limits:

1. Check Stats in Ably dashboard
2. Optimize message frequency in backend
3. Batch status updates where possible
4. Upgrade to paid tier for higher limits

## Rollback to WebSocket

If you need to rollback to the previous WebSocket implementation:

```bash
# Restore websocket.py from git
git checkout HEAD~1 backend/app/services/websocket.py

# Revert chat.py and coordinator.py changes
git checkout HEAD~1 backend/app/api/chat.py
git checkout HEAD~1 backend/app/agents/coordinator.py

# Restore frontend hooks
git checkout HEAD~1 frontend/src/hooks/useChat.ts
git checkout HEAD~1 frontend/src/pages/LandingPage.tsx
git checkout HEAD~1 frontend/src/pages/ChatView.tsx

# Remove Ably dependencies
# backend/requirements.txt: remove ably==2.0.7
# frontend/package.json: remove "ably": "^1.2.50"

# Rebuild
docker-compose up -d --build
```

## Resources

- [Ably Documentation](https://ably.com/docs)
- [Ably React Guide](https://ably.com/docs/getting-started/react)
- [Ably REST API](https://ably.com/docs/rest)
- [Ably Channels](https://ably.com/docs/realtime/channels)
- [Ably Authentication](https://ably.com/docs/realtime/authentication)

