# 🗑️ Cascade Delete Implementation

## Summary

Added CASCADE delete constraints to ensure data integrity when parent records are deleted.

---

## ✅ Changes Made

### 1. **Updated Models**

#### `backend/app/models/chat.py`

**Conversation Model:**
```python
# Before
user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id"), nullable=True)

# After
user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=True)
```

**Message Model:**
```python
# Before
conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)

# After
conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
```

### 2. **Database Migration**

Created migration file: `backend/alembic/versions/001_add_cascade_deletes.py`

This migration:
- Drops existing foreign key constraints
- Re-creates them with `ondelete='CASCADE'`
- Provides rollback capability

---

## 📊 Cascade Delete Relationships

```
User (deleted)
  └── Conversations (CASCADE deleted)
       └── Messages (CASCADE deleted)

Goal (deleted)
  └── Conversations (CASCADE deleted)
       └── Messages (CASCADE deleted)
  └── Feedback (CASCADE deleted) ✅ Already implemented

Conversation (deleted)
  └── Messages (CASCADE deleted) ✅ Already implemented
```

---

## 🔍 Already Implemented

The following models **already have** CASCADE deletes:

### `backend/app/models/feedback.py`
```python
user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
opportunity_id = Column(UUID(as_uuid=True), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
```

### `backend/app/models/goal.py`
```python
user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
```

---

## 🚀 How to Apply

### 1. **Run Migration (when database is ready)**

```bash
cd backend
alembic upgrade head
```

Or in Docker:

```bash
docker-compose exec backend alembic upgrade head
```

### 2. **Verify Changes**

Connect to PostgreSQL and check constraints:

```sql
-- Check conversations table
SELECT 
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    confrelid::regclass AS referenced_table,
    confdeltype AS delete_action
FROM pg_constraint
WHERE conrelid = 'conversations'::regclass
AND contype = 'f';

-- Check messages table
SELECT 
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    confrelid::regclass AS referenced_table,
    confdeltype AS delete_action
FROM pg_constraint
WHERE conrelid = 'messages'::regclass
AND contype = 'f';
```

Expected `delete_action` values:
- `c` = CASCADE
- `a` = NO ACTION (old behavior)

---

## 🧪 Test Scenarios

### Test 1: Delete Goal → Conversations Cascade

```python
# Create goal with conversation
goal = Goal(user_id=user_id, description="Test", goal_type=GoalType.JOB)
db.add(goal)
await db.commit()

conversation = Conversation(user_id=user_id, goal_id=goal.id)
db.add(conversation)
await db.commit()

# Delete goal
await db.delete(goal)
await db.commit()

# Verify conversation is also deleted
result = await db.execute(select(Conversation).where(Conversation.id == conversation.id))
assert result.scalar_one_or_none() is None  # Should be None
```

### Test 2: Delete User → All Related Data Cascades

```python
# Delete user
await db.delete(user)
await db.commit()

# Verify all related data is deleted
conversations = await db.execute(select(Conversation).where(Conversation.user_id == user.id))
assert len(conversations.scalars().all()) == 0

goals = await db.execute(select(Goal).where(Goal.user_id == user.id))
assert len(goals.scalars().all()) == 0

feedback = await db.execute(select(Feedback).where(Feedback.user_id == user.id))
assert len(feedback.scalars().all()) == 0
```

### Test 3: Delete Conversation → Messages Cascade

```python
# Delete conversation
await db.delete(conversation)
await db.commit()

# Verify messages are deleted
messages = await db.execute(select(Message).where(Message.conversation_id == conversation.id))
assert len(messages.scalars().all()) == 0
```

---

## ⚠️ Important Notes

### Data Integrity
- **Irreversible**: Once a parent record is deleted, all child records are permanently removed
- **No Soft Deletes**: This is a hard delete, not a soft delete (no "deleted_at" column)
- **Transaction Safety**: All deletes happen within a transaction, ensuring atomicity

### Performance
- **Database-level**: Cascading happens at the database level, not in Python
- **Fast**: More efficient than application-level deletion loops
- **Foreign Key Indexes**: Ensure foreign key columns are indexed for performance

### Circular References - FIXED ✅

**The Problem:**
- `Goal.conversation_id` → `Conversation` (nullable)
- `Conversation.goal_id` → `Goal` (nullable)

This created a circular dependency where deleting either entity could cause issues.

**The Solution:**
- **When Goal is deleted** → `Conversation` CASCADE deletes (and all its messages)
- **When Conversation is deleted** → `Goal.conversation_id` is SET to NULL (goal remains, just loses reference)

**Implementation:**
```python
# Goal model
conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)

# Conversation model  
goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=True)
```

This ensures:
1. ✅ Goals can exist without conversations
2. ✅ Deleting a goal cleans up its conversation
3. ✅ Deleting a conversation doesn't orphan the goal
4. ✅ No circular cascade loops

---

## 🔄 Rollback

If you need to revert the changes:

```bash
alembic downgrade -1
```

This will:
1. Drop CASCADE foreign keys
2. Re-create foreign keys without CASCADE
3. Restore original behavior

---

## 📝 Future Considerations

### Soft Deletes
If you need to preserve data history, consider implementing soft deletes:

```python
class Conversation(Base):
    # ... existing columns ...
    deleted_at = Column(DateTime, nullable=True)
    
    @hybrid_property
    def is_deleted(self):
        return self.deleted_at is not None
```

### Audit Trail
For compliance, consider adding an audit log table:

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    table_name = Column(String, nullable=False)
    record_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String, nullable=False)  # 'INSERT', 'UPDATE', 'DELETE'
    user_id = Column(UUID(as_uuid=True))
    data_snapshot = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## ✅ Status

- [x] Models updated with CASCADE constraints
- [x] Migration file created
- [ ] Migration applied to database (pending backend restart)
- [ ] Tests written for cascade behavior
- [ ] Documentation updated

---

**Implementation Date**: November 2025  
**Status**: Ready for deployment

