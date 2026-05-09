"""seed essential rooms

Revision ID: c1e8f3a92b05
Revises: b2f9d6b1a4c3
Create Date: 2026-05-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c1e8f3a92b05'
down_revision: Union[str, None] = '91a7dc2f4f0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ESSENTIAL_ROOMS = [
    {"id": 1, "name": "Storage"},
    {"id": 2, "name": "Sterilization"},
    {"id": 3, "name": "OR"},
]


def upgrade() -> None:
    conn = op.get_bind()
    for room in ESSENTIAL_ROOMS:
        exists = conn.execute(
            sa.text("SELECT id FROM rooms WHERE id = :id"),
            {"id": room["id"]},
        ).fetchone()
        if not exists:
            conn.execute(
                sa.text("INSERT INTO rooms (id, name) VALUES (:id, :name)"),
                room,
            )
        else:
            conn.execute(
                sa.text("UPDATE rooms SET name = :name WHERE id = :id"),
                room,
            )


def downgrade() -> None:
    pass
