"""add user_id to urls

Revision ID: b7d13ee0a4f2
Revises: ec46e3e114db
Create Date: 2026-03-20 18:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7d13ee0a4f2"
down_revision: Union[str, Sequence[str], None] = "ec46e3e114db"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("urls", sa.Column("user_id", sa.String(length=36), nullable=True))
    op.create_index(op.f("ix_urls_user_id"), "urls", ["user_id"], unique=False)
    op.create_foreign_key(
        "fk_urls_user_id_users",
        "urls",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_urls_user_id_users", "urls", type_="foreignkey")
    op.drop_index(op.f("ix_urls_user_id"), table_name="urls")
    op.drop_column("urls", "user_id")
