from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base


class ProcedureStep(Base):
    __tablename__ = "procedure_steps"
    __table_args__ = (
        UniqueConstraint("procedure_id", "step_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    procedure_id: Mapped[int] = mapped_column(ForeignKey("procedures.id"), index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    step_order: Mapped[int] = mapped_column(Integer, index=True)
    is_required: Mapped[bool] = mapped_column(default=True)
