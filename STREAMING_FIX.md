# Streaming Duplication Fix

## Problem

Streaming tokens were appearing duplicated in the UI:
```
I'd I'd love love to to help help you you find find...
```

Each word/token appeared twice.

## Root Cause

**Double Subscription Issue**: The frontend Ably hook was creating multiple subscriptions to the same channel.

### Why This Happened

1. The `connect()` function in `useAbly.ts` checked if already connected
2. If not connected, it created a NEW Ably client
3. But it didn't disconnect the OLD client first
4. Result: Multiple clients subscribing to the same channel
5. Each token was received by BOTH subscriptions → duplication

### Secondary Issue

The Ably Python SDK's `AblyRest` is synchronous, but we were using `await` on it. This could cause the publish to be called in an unexpected way.

## Fixes Applied

### 1. Frontend - Disconnect Before Reconnect

**File**: `frontend/src/hooks/useAbly.ts`

Added cleanup before creating new connection:

```typescript
// Disconnect any existing connection first
if (clientRef.current) {
  console.log('Disconnecting existing Ably client before reconnecting')
  if (channelRef.current) {
    channelRef.current.unsubscribe()
  }
  clientRef.current.close()
  clientRef.current = null
  channelRef.current = null
}
```

This ensures:
- Only ONE Ably client exists at a time
- Old subscriptions are properly cleaned up
- No duplicate event handlers

### 2. Backend - Proper Async Handling

**File**: `backend/app/services/ably_service.py`

Wrapped synchronous Ably publish calls in `run_in_executor`:

```python
await asyncio.get_event_loop().run_in_executor(
    None,
    lambda: channel.publish(name="stream_token", data={
        "message_id": message_id,
        "token": token
    })
)
```

This ensures:
- Synchronous Ably SDK calls don't block the event loop
- Proper async/await semantics
- No accidental double-calls

### 3. Backend - Enhanced Logging

**File**: `backend/app/api/chat.py`

Added detailed logging to track streaming:

```python
logger.info(f"Starting stream for conversation {conversation_id}, message {message_id}")
logger.debug(f"Token {token_count}: '{token}' (len={len(token)})")
logger.info(f"Stream complete: {token_count} tokens, {len(full_content)} chars")
```

Helps debug future issues.

## Testing

### Before Fix
```
User: "Find speaking opportunities"
Bot: "I'd I'd love love to to help help you you..."
```

### After Fix
```
User: "Find speaking opportunities"
Bot: "I'd love to help you..."
```

### How to Verify

1. Restart backend: `docker-compose restart backend worker`
2. Hard refresh frontend (Cmd+Shift+R)
3. Create new conversation
4. Watch tokens stream WITHOUT duplication
5. Check browser console:
   - Should see "Disconnecting existing Ably client..." only when needed
   - Should NOT see duplicate "Ably event: stream_token" logs for same token

6. Check backend logs:
   ```bash
   docker-compose logs -f backend | grep "Token"
   ```
   - Each token should appear once
   - Token count should match character count

## Additional Improvements

### Connection Management

The fix also improves overall connection management:
- Prevents memory leaks from abandoned connections
- Ensures clean state transitions
- Better error recovery

### Performance

- Reduced network overhead (no duplicate messages)
- Lower CPU usage (no duplicate event processing)
- Cleaner state management

## Related Files

- `backend/app/services/ably_service.py` - Async executor wrapper
- `backend/app/api/chat.py` - Enhanced logging
- `frontend/src/hooks/useAbly.ts` - Connection cleanup
- `frontend/src/pages/LandingPage.tsx` - Streaming display
- `frontend/src/pages/ChatView.tsx` - Streaming display

## Lessons Learned

1. **Always clean up before creating new connections**
   - Especially important with real-time systems
   - Prevents resource leaks and duplicate handlers

2. **Match async/sync semantics properly**
   - Don't `await` synchronous code
   - Use `run_in_executor` for sync code in async context

3. **Add logging for debugging**
   - Token counts help verify correctness
   - Connection state logs help track issues

4. **Test with fresh state**
   - Hard refresh to clear any cached connections
   - Restart backend to ensure clean state

---

**Status**: ✅ Fixed

Streaming now works correctly with no duplication!

