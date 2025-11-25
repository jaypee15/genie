"""make timestamps timezone aware

Revision ID: 002
Revises: 001
Create Date: 2025-11-25 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Alter timestamp columns to be timezone-aware (TIMESTAMPTZ in PostgreSQL)
    # PostgreSQL will automatically convert existing TIMESTAMP to TIMESTAMPTZ, treating existing values as UTC
    
    # Conversations table
    op.alter_column('conversations', 'created_at',
                    type_=sa.DateTime(timezone=True),
                    existing_type=sa.DateTime(),
                    existing_nullable=False)
    op.alter_column('conversations', 'updated_at',
                    type_=sa.DateTime(timezone=True),
                    existing_type=sa.DateTime(),
                    existing_nullable=False)
    
    # Messages table
    op.alter_column('messages', 'created_at',
                    type_=sa.DateTime(timezone=True),
                    existing_type=sa.DateTime(),
                    existing_nullable=False)


def downgrade():
    # Revert to timezone-naive timestamps
    op.alter_column('messages', 'created_at',
                    type_=sa.DateTime(),
                    existing_type=sa.DateTime(timezone=True),
                    existing_nullable=False)
    
    op.alter_column('conversations', 'updated_at',
                    type_=sa.DateTime(),
                    existing_type=sa.DateTime(timezone=True),
                    existing_nullable=False)
    op.alter_column('conversations', 'created_at',
                    type_=sa.DateTime(),
                    existing_type=sa.DateTime(timezone=True),
                    existing_nullable=False)

