import os


DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./weathernova_local.db"

SQL_ECHO = os.getenv(
    "SQL_ECHO",
    "",
).lower() in {
    "1",
    "true",
    "yes",
    "on",
}
