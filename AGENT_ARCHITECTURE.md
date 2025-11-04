# Genie Agent Architecture

## Design Principle: Single User-Facing Agent

Genie uses a **Clarifier-First Architecture** where all user communication flows through a single agent, ensuring consistent, friendly, and contextual interactions.

## Agent Roles

### 1. 🗣️ Clarifier Agent (USER-FACING)

**The ONLY agent that communicates directly with users.**

**Responsibilities:**
- ✅ Receive all user inputs
- ✅ Clarify and structure user goals
- ✅ Format all responses to users
- ✅ Provide friendly acknowledgments
- ✅ Explain system actions
- ✅ Handle errors gracefully

**Key Methods:**
```python
# Input Processing
async def clarify_goal(user_input: str) -> Dict
async def generate_clarifying_questions(goal: str) -> List[str]
async def refine_goal_with_answers(goal: Dict, answers: List) -> Dict

# Output Formatting (All user messages go through these)
async def format_results_for_user(count: int, summary: str, status: str) -> str
async def acknowledge_feedback(rating: int) -> str
async def explain_goal_clarification(structured_goal: Dict) -> str
```

**Example User Interactions:**
```python
# User creates goal
"I understand you're looking for job opportunities related to AI, machine learning in Remote positions.
I'll search across multiple platforms and notify you when I find relevant opportunities."

# Results ready
"Great news! I found 42 opportunities for you.

Here are the top matches:
- 15 remote AI/ML engineering positions
- 12 data science roles at startups
- 10 research positions
- 5 consulting opportunities

You can now browse the results and provide feedback to help me improve future searches!"

# User gives feedback
"Thanks for the feedback! I'll prioritize similar opportunities in the future."
```

### 2. 🔍 Executor Agent (INTERNAL)

**Never communicates with users directly.**

**Responsibilities:**
- Execute scraping across multiple sources
- Normalize and store opportunities
- Generate embeddings
- Log scraping status
- Handle scraper failures

**Communication:**
- Reports to → Coordinator Agent
- Results processed by → Ranker Agent
- Never → Direct to user

### 3. 🎯 Ranker Agent (INTERNAL)

**Never communicates with users directly.**

**Responsibilities:**
- Perform vector similarity search
- Apply feedback weights
- Rank opportunities by relevance
- Generate technical summaries
- Filter by thresholds

**Communication:**
- Receives data from → Executor Agent
- Reports to → Coordinator Agent
- Summary formatted by → Clarifier Agent for users

### 4. 🎭 Coordinator Agent (ORCHESTRATOR)

**Routes all user communication through Clarifier Agent.**

**Responsibilities:**
- Orchestrate workflow between agents
- Manage state and error handling
- **Route all user messages through Clarifier**
- Ensure consistent user experience

**Communication Flow:**
```
User Input
    ↓
Clarifier Agent (receives and processes)
    ↓
Coordinator Agent (orchestrates)
    ↓
Executor Agent → Ranker Agent (work internally)
    ↓
Coordinator Agent (receives results)
    ↓
Clarifier Agent (formats for user)
    ↓
User Output
```

## Communication Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                         USER                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ All user communication
                     ↓
            ┌────────────────────┐
            │  Clarifier Agent   │  ← ONLY user-facing agent
            │  (User Interface)  │
            └────────┬───────────┘
                     │
                     │ Structured goals & formatted results
                     ↓
            ┌────────────────────┐
            │ Coordinator Agent  │  ← Orchestrates workflow
            └────────┬───────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ↓                     ↓
   ┌─────────────┐      ┌─────────────┐
   │  Executor   │      │   Ranker    │  ← Internal agents
   │   Agent     │──────→   Agent     │  ← Never talk to users
   └─────────────┘      └─────────────┘
          │                     │
          └──────────┬──────────┘
                     │
                     │ Results
                     ↓
            ┌────────────────────┐
            │ Coordinator Agent  │
            └────────┬───────────┘
                     │
                     │ Raw results
                     ↓
            ┌────────────────────┐
            │  Clarifier Agent   │  ← Formats for user
            └────────┬───────────┘
                     │
                     │ User-friendly message
                     ↓
┌────────────────────────────────────────────────────────┐
│                         USER                           │
└────────────────────────────────────────────────────────┘
```

## User Message Types

All messages formatted by Clarifier Agent:

### 1. Goal Acknowledgment
```
"I understand you're looking for [type] opportunities related to [keywords] in [location].
I'll search across multiple platforms and notify you when I find relevant opportunities."
```

### 2. Processing Status
```
"I'm searching for opportunities that match your goal. This may take 30-60 seconds..."
```

### 3. Results Summary
```
"Great news! I found [N] opportunities for you.

[Summary of top results]

You can now browse the results and provide feedback!"
```

### 4. No Results
```
"I couldn't find any opportunities matching your criteria right now.

Try:
- Broadening your search terms
- Removing location restrictions
- Trying a different opportunity type

I'll keep monitoring for new opportunities!"
```

### 5. Feedback Acknowledgment
```
Positive: "Thanks for the feedback! I'll prioritize similar opportunities in the future."
Negative: "Thanks for letting me know. I'll adjust my search to find better matches."
```

### 6. Error Handling
```
"I encountered an issue while searching. Please try again or refine your goal."
```

## Implementation Guidelines

### ✅ DO:

1. **Always route user messages through Clarifier:**
   ```python
   # Coordinator
   user_message = await self.clarifier.format_results_for_user(...)
   return {"user_message": user_message, ...}
   ```

2. **Use Clarifier for all user-facing text:**
   ```python
   acknowledgment = await self.clarifier.acknowledge_feedback(rating)
   explanation = await self.clarifier.explain_goal_clarification(goal)
   ```

3. **Keep internal agents focused on their tasks:**
   ```python
   # Executor - just does the work
   opportunities = await self.executor.execute_search(db, goal)
   
   # Ranker - just ranks
   ranked = await self.ranker.rank_opportunities(db, goal_id, user_id)
   ```

### ❌ DON'T:

1. **Never let internal agents generate user messages:**
   ```python
   # BAD - Executor talking to user
   return {"message": "Found 10 opportunities"}
   
   # GOOD - Through Clarifier
   msg = await clarifier.format_results_for_user(10)
   return {"user_message": msg}
   ```

2. **Never bypass Clarifier for user communication:**
   ```python
   # BAD - Direct user message
   return {"message": "Search failed"}
   
   # GOOD - Through Clarifier
   msg = await clarifier.format_results_for_user(0, status="error")
   return {"user_message": msg}
   ```

3. **Never mix internal and user-facing communication:**
   ```python
   # BAD - Mixing contexts
   return {
       "debug_info": "Scraped 3 sources",  # Internal
       "message": "Found opportunities"     # User-facing - wrong!
   }
   
   # GOOD - Separated
   logger.info("Scraped 3 sources")  # Internal logging
   msg = await clarifier.format_results_for_user(...)  # User message
   return {"user_message": msg}
   ```

## Benefits of This Architecture

### 1. **Consistency**
- All user messages have the same friendly, helpful tone
- Consistent formatting and structure
- Brand voice maintained throughout

### 2. **Maintainability**
- Single place to update user-facing text
- Easy to localize or A/B test messages
- Clear separation of concerns

### 3. **Context Awareness**
- Clarifier can maintain conversation context
- Personalize messages based on user history
- Adapt tone based on situation

### 4. **Error Handling**
- Graceful error messages
- Never expose internal errors to users
- Always provide helpful next steps

### 5. **Testing**
- Easy to test user interactions
- Mock only the Clarifier for UI tests
- Internal agents tested independently

## Example: Complete Flow

```python
# 1. USER: "Find remote AI jobs"
#    ↓
# 2. CLARIFIER: Receives input
goal = await clarifier.clarify_goal("Find remote AI jobs")
explanation = await clarifier.explain_goal_clarification(goal)
# Returns: "I understand you're looking for job opportunities..."

# 3. COORDINATOR: Orchestrates
processing_msg = await clarifier.format_results_for_user(0, status="processing")
# Returns: "I'm searching for opportunities..."

# 4. EXECUTOR: Scrapes (internal, no user messages)
opportunities = await executor.execute_search(db, goal)

# 5. RANKER: Ranks (internal, no user messages)
ranked = await ranker.rank_opportunities(db, goal_id, user_id)
summary = await ranker.generate_summary(ranked)  # Technical summary

# 6. CLARIFIER: Formats results
user_msg = await clarifier.format_results_for_user(
    len(ranked), 
    summary,
    status="completed"
)
# Returns: "Great news! I found 42 opportunities..."

# 7. USER: Receives friendly message
```

## Key Takeaway

**The Clarifier Agent is the friendly face of Genie.**

All user interaction flows through it, ensuring every message is:
- ✅ Friendly and helpful
- ✅ Contextually appropriate
- ✅ Actionable
- ✅ Consistent with brand voice
- ✅ Never exposing internal details

**Internal agents (Executor, Ranker) focus on their specialized tasks and never talk to users directly.**

