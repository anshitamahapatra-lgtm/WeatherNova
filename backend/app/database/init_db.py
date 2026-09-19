from backend.app.database.base import Base
from backend.app.database.connection import engine
from backend.app.models import WeatherReport, WeatherEvent


def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("WeatherNova database tables recreated successfully")


if __name__ == "__main__":
    init_db()