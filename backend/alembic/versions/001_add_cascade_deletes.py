"""add cascade deletes to conversations and messages

Revision ID: 001
Revises: 
Create Date: 2025-11-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing foreign key constraints
    op.drop_constraint('conversations_goal_id_fkey', 'conversations', type_='foreignkey')
    op.drop_constraint('conversations_user_id_fkey', 'conversations', type_='foreignkey')
    op.drop_constraint('messages_conversation_id_fkey', 'messages', type_='foreignkey')
    op.drop_constraint('goals_conversation_id_fkey', 'goals', type_='foreignkey')
    
    # Re-create foreign key constraints with CASCADE delete
    op.create_foreign_key(
        'conversations_goal_id_fkey',
        'conversations', 'goals',
        ['goal_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'conversations_user_id_fkey',
        'conversations', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'messages_conversation_id_fkey',
        'messages', 'conversations',
        ['conversation_id'], ['id'],
        ondelete='CASCADE'
    )
    # Fix circular reference: When conversation is deleted, set goal's conversation_id to NULL
    op.create_foreign_key(
        'goals_conversation_id_fkey',
        'goals', 'conversations',
        ['conversation_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Drop CASCADE foreign key constraints
    op.drop_constraint('conversations_goal_id_fkey', 'conversations', type_='foreignkey')
    op.drop_constraint('conversations_user_id_fkey', 'conversations', type_='foreignkey')
    op.drop_constraint('messages_conversation_id_fkey', 'messages', type_='foreignkey')
    op.drop_constraint('goals_conversation_id_fkey', 'goals', type_='foreignkey')
    
    # Re-create foreign key constraints without CASCADE
    op.create_foreign_key(
        'conversations_goal_id_fkey',
        'conversations', 'goals',
        ['goal_id'], ['id']
    )
    op.create_foreign_key(
        'conversations_user_id_fkey',
        'conversations', 'users',
        ['user_id'], ['id']
    )
    op.create_foreign_key(
        'messages_conversation_id_fkey',
        'messages', 'conversations',
        ['conversation_id'], ['id']
    )
    op.create_foreign_key(
        'goals_conversation_id_fkey',
        'goals', 'conversations',
        ['conversation_id'], ['id']
    )

