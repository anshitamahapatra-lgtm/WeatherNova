from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.config import DATABASE_URL
from app.database.config import SQL_ECHO


engine = create_engine(
    DATABASE_URL,
    echo=SQL_ECHO,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
