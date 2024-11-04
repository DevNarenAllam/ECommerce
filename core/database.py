from sqlmodel import create_engine, Session
from core.config import DATABASE_URL
from typing import Generator

engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20, future=True)


# Function to get a session
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
