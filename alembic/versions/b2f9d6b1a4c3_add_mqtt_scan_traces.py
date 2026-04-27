"""add mqtt scan traces

Revision ID: b2f9d6b1a4c3
Revises: 6c8f0c5d9f5a
Create Date: 2026-04-26 20:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2f9d6b1a4c3"
down_revision: Union[str, None] = "6c8f0c5d9f5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mqtt_scan_traces",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.String(length=200), nullable=False),
        sa.Column("device_mac", sa.String(length=64), nullable=False),
        sa.Column("rfid_uid", sa.String(length=64), nullable=True),
        sa.Column("scanned_at", sa.DateTime(), nullable=True),
        sa.Column("backend_received_at", sa.DateTime(), nullable=False),
        sa.Column("handler_started_at", sa.DateTime(), nullable=False),
        sa.Column("handler_finished_at", sa.DateTime(), nullable=True),
        sa.Column("outcome", sa.String(length=64), nullable=False),
        sa.Column("instrument_id", sa.Integer(), nullable=True),
        sa.Column("from_room_id", sa.Integer(), nullable=True),
        sa.Column("to_room_id", sa.Integer(), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_detail", sa.String(length=500), nullable=True),
        sa.Column("raw_topic", sa.String(length=255), nullable=False),
        sa.Column("raw_payload", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("mqtt_scan_traces", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_mqtt_scan_traces_backend_received_at"), ["backend_received_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_mqtt_scan_traces_device_mac"), ["device_mac"], unique=False)
        batch_op.create_index(batch_op.f("ix_mqtt_scan_traces_event_id"), ["event_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_mqtt_scan_traces_instrument_id"), ["instrument_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_mqtt_scan_traces_outcome"), ["outcome"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("mqtt_scan_traces", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_mqtt_scan_traces_outcome"))
        batch_op.drop_index(batch_op.f("ix_mqtt_scan_traces_instrument_id"))
        batch_op.drop_index(batch_op.f("ix_mqtt_scan_traces_event_id"))
        batch_op.drop_index(batch_op.f("ix_mqtt_scan_traces_device_mac"))
        batch_op.drop_index(batch_op.f("ix_mqtt_scan_traces_backend_received_at"))

    op.drop_table("mqtt_scan_traces")
