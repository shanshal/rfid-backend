from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base


class ProcedureStep(Base):
    __tablename__ = "procedure_steps"

    # Table: procedure_steps
    # Properties:
    # - id: primary key
    # - procedure_id: foreign key to procedures.id
    # - room_id: foreign key to rooms.id
    # - step_order: strict order in the procedure
    # - is_required: whether this step is mandatory

    id: Mapped[int] = mapped_column(primary_key=True)
    procedure_id: Mapped[int] = mapped_column(ForeignKey("procedures.id"), index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    step_order: Mapped[int] = mapped_column(Integer, index=True)

    # TODO: Add uniqueness constraint on (procedure_id, step_order).
    # TODO: Add required/optional step flag.
