from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.db.session import Base

class Kit(Base):
    __tablename__ = "kits"

    # Table: kits
    # Properties:
    # - id: primary key
    # - name: kit name
    # - deleted_at: soft delete timestamp

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)

    # TODO: Kit membership with instruments is many-to-many.
    # TODO: Implement via a dedicated association table.
    # TODO: Soft delete applies to kits to preserve audit history.
