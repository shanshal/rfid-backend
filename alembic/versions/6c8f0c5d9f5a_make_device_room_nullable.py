"""make device room nullable

Revision ID: 6c8f0c5d9f5a
Revises: 5390d0c86915
Create Date: 2026-04-26 17:38:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6c8f0c5d9f5a"
down_revision: Union[str, None] = "5390d0c86915"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("devices", schema=None) as batch_op:
        batch_op.alter_column("room_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("devices", schema=None) as batch_op:
        batch_op.alter_column("room_id", existing_type=sa.Integer(), nullable=False)
