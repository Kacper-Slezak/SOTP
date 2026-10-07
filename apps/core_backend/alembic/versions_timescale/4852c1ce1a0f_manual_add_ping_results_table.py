"""manual_add_ping_results_table

Revision ID: 4852c1ce1a0f
Revises: 0001_init_timescale
Create Date: 2025-11-02 17:40:32.123456

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4852c1ce1a0f"
down_revision: str | None = "0001_init_timescale"
# Fix: Changed ('timescale',) to None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### Start of manually added code ###
    op.create_table(
        "ping_results",
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=False),
        sa.Column("is_alive", sa.Boolean(), nullable=False),
        sa.Column("rtt_avg_ms", sa.Float(), nullable=True),
        sa.Column("packet_loss_percent", sa.Float(), nullable=True),
        sa.Column("diagnostic_message", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("timestamp", "device_id"),
    )
    op.create_index(
        op.f("ix_ping_results_device_id"), "ping_results", ["device_id"], unique=False
    )
    op.create_index(
        op.f("ix_ping_results_is_alive"), "ping_results", ["is_alive"], unique=False
    )

    # Manually added step for hypertable
    op.execute("SELECT create_hypertable('ping_results', 'timestamp');")
    # ### End of manually added code ###


def downgrade() -> None:
    # ### Start of manually added code ###
    op.drop_index(op.f("ix_ping_results_is_alive"), table_name="ping_results")
    op.drop_index(op.f("ix_ping_results_device_id"), table_name="ping_results")
    op.drop_table("ping_results")
    # ### End of manually added code ###
