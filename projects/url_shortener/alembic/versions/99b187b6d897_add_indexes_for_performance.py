"""add_indexes_for_performance

Revision ID: 99b187b6d897
Revises: affa2455cc19
Create Date: 2026-03-03 00:18:58.026014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99b187b6d897'
down_revision: Union[str, Sequence[str], None] = 'affa2455cc19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add index on is_active for faster filtering
    op.create_index("ix_urls_is_active", "urls", ["is_active"])
    
    # Add composite index on (original_url, is_active) for get_by_original_url query
    op.create_index("ix_urls_original_url_is_active", "urls", ["original_url", "is_active"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_urls_original_url_is_active", table_name="urls")
    op.drop_index("ix_urls_is_active", table_name="urls")
