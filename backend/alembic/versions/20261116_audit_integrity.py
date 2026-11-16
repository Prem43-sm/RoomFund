"""add immutable audit event snapshots and integrity hashes

Revision ID: 20261116_audit_integrity
Revises: 20261116_workspace_privacy
"""
from alembic import op
import sqlalchemy as sa

revision = "20261116_audit_integrity"
down_revision = "20261116_workspace_privacy"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("audit_logs", sa.Column("before_data", sa.Text(), nullable=True))
    op.add_column("audit_logs", sa.Column("after_data", sa.Text(), nullable=True))
    op.add_column("audit_logs", sa.Column("previous_hash", sa.String(length=64), nullable=True))
    op.add_column("audit_logs", sa.Column("record_hash", sa.String(length=64), nullable=True))
    op.create_index("uq_audit_logs_record_hash", "audit_logs", ["record_hash"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_audit_logs_record_hash", table_name="audit_logs")
    op.drop_column("audit_logs", "record_hash")
    op.drop_column("audit_logs", "previous_hash")
    op.drop_column("audit_logs", "after_data")
    op.drop_column("audit_logs", "before_data")
