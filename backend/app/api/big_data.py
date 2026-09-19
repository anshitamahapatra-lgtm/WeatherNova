from fastapi import APIRouter


router = APIRouter(
    prefix="/big-data",
    tags=["Big Data"],
)


@router.get("/pipeline")
def get_pipeline_status():
    return {
        "ingestion": {
            "weather_api": "implemented",
            "citizen_reports": "implemented",
            "public_datasets": "architecture_ready",
            "web_sources": "architecture_ready",
            "social_media": "requires_external_credentials",
        },
        "streaming": {
            "kafka": "architecture_documented",
            "spark": "architecture_documented",
            "status": "not_connected_in_runtime",
        },
        "storage": {
            "primary_database": "postgresql_or_sqlite",
            "safe_migrations": "additive_create_all",
        },
        "analytics": {
            "dashboard_summary": "implemented",
            "map_reports": "implemented",
            "event_distribution": "implemented",
        },
    }
