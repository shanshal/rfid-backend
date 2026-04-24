from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base


class Procedure(Base):
    __tablename__ = "procedures"

    # Table: procedures
    # Properties:
    # - id: primary key
    # - name: unique procedure name
    # - description: optional notes
    # - is_active: active flag
    # - deleted_at: soft delete timestamp

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # TODO: Add optional description, is_active, deleted_at columns.
