import os


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Anshita%402004@localhost:5432/weathernova",
)