from collections.abc import Generator

from sqlalchemy.orm import Session

from src.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    # TODO: Keep as shared FastAPI dependency for all routes.
    # TODO: Add logging/metrics hooks around DB sessions if needed.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
