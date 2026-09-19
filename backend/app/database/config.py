import os


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Anshita%402004@localhost:5432/weathernova",
)

SQL_ECHO = os.getenv(
    "SQL_ECHO",
    "",
).lower() in {
    "1",
    "true",
    "yes",
    "on",
}
