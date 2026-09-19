import os
import socket
from datetime import datetime
from urllib.parse import urlparse

import requests
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import IngestionJob


router = APIRouter(
    prefix="/big-data",
    tags=["Big Data"],
)


def split_csv(value):
    return [
        item.strip()
        for item in (value or "").split(",")
        if item.strip()
    ]


def env_flag(name):
    return os.getenv(name, "").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def check_socket(endpoint):
    host, _, port = endpoint.partition(":")

    if not host or not port.isdigit():
        return {
            "state": "CONFIGURED",
            "detail": "Configured, but bootstrap endpoint format could not be runtime-checked.",
        }

    try:
        with socket.create_connection(
            (host, int(port)),
            timeout=2,
        ):
            return {
                "state": "READY",
                "detail": "Runtime endpoint accepted a TCP connection.",
            }
    except OSError as exc:
        return {
            "state": "NOT_RUNNING",
            "detail": f"Configured, but runtime check failed: {exc}.",
        }


def check_http(url):
    try:
        response = requests.get(
            url,
            timeout=3,
        )

        if response.status_code < 500:
            return {
                "state": "READY",
                "detail": "Runtime endpoint returned an HTTP response.",
            }
    except requests.RequestException as exc:
        return {
            "state": "NOT_RUNNING",
            "detail": f"Configured, but runtime check failed: {exc}.",
        }

    return {
        "state": "NOT_RUNNING",
        "detail": "Configured, but runtime endpoint returned a server error.",
    }


def configured_status(configured, ready=False):
    if ready:
        return "READY"

    return "CONFIGURED" if configured else "NOT_CONFIGURED"


def social_media_status():
    provider = os.getenv("SOCIAL_MEDIA_PROVIDER", "").strip()
    token = os.getenv("SOCIAL_MEDIA_BEARER_TOKEN", "").strip()
    hashtags = split_csv(
        os.getenv("SOCIAL_HASHTAGS", "#IMD,#Weather,#RainAlert")
    )

    configured = bool(provider and token)

    return {
        "name": "Social Media Hashtag Connector",
        "state": configured_status(configured),
        "provider": provider or None,
        "hashtags": hashtags,
        "auth_required": True,
        "source": "configured_connector" if configured else "not_configured",
        "detail": (
            "Connector configuration is present; live ingestion can be run by a provider-specific worker."
            if configured
            else "Set SOCIAL_MEDIA_PROVIDER and SOCIAL_MEDIA_BEARER_TOKEN to enable real hashtag ingestion. No live social data is fabricated."
        ),
    }


def public_ingestion_status():
    dataset_urls = split_csv(os.getenv("PUBLIC_DATASET_URLS", ""))
    api_urls = split_csv(os.getenv("PUBLIC_API_URLS", ""))
    website_urls = split_csv(os.getenv("PUBLIC_WEBSITE_URLS", ""))
    configured = bool(dataset_urls or api_urls or website_urls)

    return {
        "name": "Public Dataset / Website / API Ingestion",
        "state": configured_status(configured),
        "dataset_urls": dataset_urls,
        "api_urls": api_urls,
        "website_urls": website_urls,
        "detail": (
            "External public sources are configured for ingestion jobs."
            if configured
            else "No public dataset, website, or API ingestion sources are configured. Existing Open-Meteo weather API ingestion remains active."
        ),
    }


def kafka_status():
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "").strip()
    topic = os.getenv(
        "KAFKA_WEATHER_TOPIC",
        "weathernova.weather.reports",
    )

    if not bootstrap:
        return {
            "name": "Kafka Streaming Runtime",
            "state": "NOT_CONFIGURED",
            "bootstrap_servers": None,
            "topic": topic,
            "detail": "Set KAFKA_BOOTSTRAP_SERVERS to enable Kafka streaming integration.",
        }

    if env_flag("KAFKA_SKIP_RUNTIME_CHECK"):
        return {
            "name": "Kafka Streaming Runtime",
            "state": "CONFIGURED",
            "bootstrap_servers": bootstrap,
            "topic": topic,
            "detail": "Configured; runtime check skipped by KAFKA_SKIP_RUNTIME_CHECK.",
        }

    first_endpoint = split_csv(bootstrap)[0]
    check = check_socket(first_endpoint)

    return {
        "name": "Kafka Streaming Runtime",
        "state": check["state"],
        "bootstrap_servers": bootstrap,
        "topic": topic,
        "detail": check["detail"],
    }


def spark_status():
    master_url = os.getenv("SPARK_MASTER_URL", "").strip()

    if not master_url:
        return {
            "name": "Spark Processing Runtime",
            "state": "NOT_CONFIGURED",
            "master_url": None,
            "detail": "Set SPARK_MASTER_URL to enable Spark processing integration.",
        }

    if env_flag("SPARK_SKIP_RUNTIME_CHECK"):
        return {
            "name": "Spark Processing Runtime",
            "state": "CONFIGURED",
            "master_url": master_url,
            "detail": "Configured; runtime check skipped by SPARK_SKIP_RUNTIME_CHECK.",
        }

    parsed = urlparse(master_url)

    if parsed.scheme in {"http", "https"}:
        check = check_http(master_url)
    else:
        endpoint = parsed.netloc or master_url.replace("spark://", "")
        check = check_socket(endpoint)

    return {
        "name": "Spark Processing Runtime",
        "state": check["state"],
        "master_url": master_url,
        "detail": check["detail"],
    }


def media_storage_status():
    provider = os.getenv("MEDIA_STORAGE_PROVIDER", "").strip()
    base_url = os.getenv("MEDIA_STORAGE_BASE_URL", "").strip()
    configured = bool(provider and base_url)

    return {
        "name": "Media Storage",
        "state": configured_status(configured),
        "provider": provider or None,
        "base_url": base_url or None,
        "detail": (
            "Media storage is configured for URL/reference metadata."
            if configured
            else "Binary upload/storage is not configured. Citizen reports accept safe photo/video URLs as external references only."
        ),
    }


def pipeline_payload():
    social = social_media_status()
    public_sources = public_ingestion_status()
    kafka = kafka_status()
    spark = spark_status()
    media = media_storage_status()

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "ingestion": {
            "weather_api": "READY",
            "citizen_reports": "READY",
            "public_datasets": public_sources["state"],
            "web_sources": public_sources["state"],
            "public_apis": public_sources["state"],
            "social_media": social["state"],
        },
        "connectors": [
            social,
            public_sources,
            media,
        ],
        "streaming": {
            "kafka": kafka,
            "spark": spark,
        },
        "storage": {
            "primary_database": "postgresql_or_sqlite",
            "safe_migrations": "additive_create_all_plus_missing_columns",
            "media_storage": media["state"],
        },
        "analytics": {
            "dashboard_summary": "READY",
            "map_reports": "READY",
            "event_distribution": "READY",
            "verification_signals": "HEURISTIC_PROTOTYPE",
        },
        "production_scale_note": (
            "The application exposes scalable ingestion and processing integration points. "
            "Kafka, Spark, social APIs, and external public sources require real deployed infrastructure/credentials before they are live."
        ),
    }


@router.get("/pipeline")
def get_pipeline_status():
    return pipeline_payload()


@router.get("/ingestion-jobs")
def get_ingestion_jobs(
    db: Session = Depends(get_db),
):
    jobs = (
        db.query(IngestionJob)
        .order_by(IngestionJob.started_at.desc())
        .limit(50)
        .all()
    )

    return jobs


@router.post("/ingestion-jobs")
def register_ingestion_job(
    payload: dict,
    db: Session = Depends(get_db),
):
    source_type = payload.get("source_type", "public_api")
    source_name = payload.get("source_name", source_type)

    job = IngestionJob(
        source_type=source_type,
        source_name=source_name,
        source_url=payload.get("source_url"),
        connector_status=payload.get("connector_status", "CONFIGURED"),
        status=payload.get("status", "registered"),
        records_seen=int(payload.get("records_seen", 0)),
        records_created=int(payload.get("records_created", 0)),
        notes=payload.get(
            "notes",
            "Registered configuration only; no external data was fetched by this endpoint.",
        ),
        finished_at=None,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job
