"""add workspace location and identity provider without rewriting existing data

Revision ID: 20261116_workspace_privacy
Revises: be1363324672
Create Date: 2026-11-16
"""
from alembic import op
import sqlalchemy as sa

revision = "20261116_workspace_privacy"
down_revision = "be1363324672"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("rooms", sa.Column("location", sa.String(length=500), nullable=True))
    op.add_column("users", sa.Column("auth_provider", sa.String(length=30), nullable=False, server_default="password"))


def downgrade() -> None:
    op.drop_column("users", "auth_provider")
    op.drop_column("rooms", "location")
