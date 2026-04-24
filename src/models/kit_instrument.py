from sqlalchemy import ForeignKey, Table, Column, Integer

from src.db.session import Base


# Table: kit_instruments (association table)
# Properties:
# - kit_id: foreign key to kits.id
# - instrument_id: foreign key to instruments.id
# - linked_at: UTC timestamp when membership is created
kit_instruments = Table(
    "kit_instruments",
    Base.metadata,
    Column("kit_id", Integer, ForeignKey("kits.id"), primary_key=True),
    Column("instrument_id", Integer, ForeignKey("instruments.id"), primary_key=True),
)
