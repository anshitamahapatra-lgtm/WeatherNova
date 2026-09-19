from app.database.base import Base
from app.database.connection import engine
from app.models import WeatherReport, WeatherEvent


def init_db():
    Base.metadata.create_all(bind=engine)
    print("WeatherNova database tables initialized successfully")


if __name__ == "__main__":
    init_db()