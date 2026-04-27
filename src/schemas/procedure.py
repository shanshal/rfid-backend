from pydantic import BaseModel


class ProcedureCreate(BaseModel):
    name: str
    description: str | None = None
    is_active: bool = True
    room_ids: list[int]


class ProcedureOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class ProcedureStepOut(BaseModel):
    id: int
    procedure_id: int
    room_id: int
    step_order: int
    is_required: bool

    model_config = {"from_attributes": True}
