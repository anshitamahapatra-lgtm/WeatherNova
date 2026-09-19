from sqlalchemy import inspect, text

from app.database.base import Base
from app.database.connection import engine
from app.models import AuditLog, IngestionJob, Source, WeatherEvent, WeatherReport


REPORT_COLUMN_SQL = {
    "external_id": "VARCHAR(160)",
    "source_url": "VARCHAR(500)",
    "media_urls": "TEXT DEFAULT '[]'",
    "hashtags": "TEXT DEFAULT '[]'",
    "raw_payload": "TEXT DEFAULT '{}'",
    "verification_notes": "TEXT DEFAULT ''",
    "misinformation_score": "FLOAT DEFAULT 0.0",
}

SOURCE_COLUMN_SQL = {
    "config_url": "VARCHAR(500)",
    "auth_required": "BOOLEAN DEFAULT FALSE",
    "runtime_status": "VARCHAR(50) DEFAULT 'NOT_CONFIGURED'",
    "status_notes": "TEXT DEFAULT ''",
}

INGESTION_JOB_COLUMN_SQL = {
    "source_url": "VARCHAR(500)",
    "connector_status": "VARCHAR(50) DEFAULT 'NOT_CONFIGURED'",
}


def add_missing_columns(table_name, column_sql):
    inspector = inspect(engine)

    if table_name not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns(table_name)
    }

    missing_columns = [
        (name, column_type)
        for name, column_type in column_sql.items()
        if name not in existing_columns
    ]

    if not missing_columns:
        return

    with engine.begin() as connection:
        for name, column_type in missing_columns:
            connection.execute(
                text(
                    f"ALTER TABLE {table_name} "
                    f"ADD COLUMN {name} {column_type}"
                )
            )


def add_missing_report_columns():
    add_missing_columns("weather_reports", REPORT_COLUMN_SQL)


def add_missing_source_columns():
    add_missing_columns("weather_sources", SOURCE_COLUMN_SQL)


def add_missing_ingestion_job_columns():
    add_missing_columns("ingestion_jobs", INGESTION_JOB_COLUMN_SQL)


def init_db():
    Base.metadata.create_all(bind=engine)
    add_missing_report_columns()
    add_missing_source_columns()
    add_missing_ingestion_job_columns()
    print("WeatherNova database tables initialized successfully")


if __name__ == "__main__":
    init_db()
