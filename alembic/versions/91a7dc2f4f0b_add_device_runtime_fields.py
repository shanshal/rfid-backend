"""add device runtime fields

Revision ID: 91a7dc2f4f0b
Revises: b2f9d6b1a4c3
Create Date: 2026-04-28 11:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "91a7dc2f4f0b"
down_revision: Union[str, None] = "b2f9d6b1a4c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("devices", schema=None) as batch_op:
        batch_op.add_column(sa.Column("local_ip", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("scan_topic", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("status_topic", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("mqtt_host", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("mqtt_port", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("firmware", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("last_status", sa.String(length=32), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("devices", schema=None) as batch_op:
        batch_op.drop_column("last_status")
        batch_op.drop_column("firmware")
        batch_op.drop_column("mqtt_port")
        batch_op.drop_column("mqtt_host")
        batch_op.drop_column("status_topic")
        batch_op.drop_column("scan_topic")
        batch_op.drop_column("local_ip")
