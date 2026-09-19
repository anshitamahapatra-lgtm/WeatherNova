import json
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.ml.duplicate_detector import is_duplicate_report
from app.ml.source_reliability import get_source_reliability
from app.models.report import WeatherReport


MEDIA_EXTENSIONS = {
    "photo": (".jpg", ".jpeg", ".png", ".webp", ".gif"),
    "video": (".mp4", ".mov", ".webm", ".m4v"),
}


def parse_json_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str):
        stripped = value.strip()

        if not stripped:
            return []

        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            parsed = [
                item.strip()
                for item in stripped.split(",")
            ]

        if isinstance(parsed, list):
            return [
                str(item).strip()
                for item in parsed
                if str(item).strip()
            ]

    return []


def dump_json(value):
    return json.dumps(value or [], ensure_ascii=True)


def safe_http_url(value):
    if not value:
        return None

    parsed = urlparse(str(value).strip())

    if parsed.scheme not in {"http", "https"}:
        return None

    if not parsed.netloc:
        return None

    return parsed.geturl()


def normalize_media_urls(value):
    media_urls = []

    for raw_url in parse_json_list(value):
        url = safe_http_url(raw_url)

        if url:
            media_urls.append(url)

    return media_urls[:8]


def classify_media(url):
    path = urlparse(url).path.lower()

    for media_type, extensions in MEDIA_EXTENSIONS.items():
        if path.endswith(extensions):
            return media_type

    return "reference"


def build_media_metadata(media_urls):
    return [
        {
            "url": url,
            "type": classify_media(url),
            "storage": "external_reference",
        }
        for url in media_urls
    ]


def normalize_hashtags(value):
    tags = []

    for tag in parse_json_list(value):
        normalized = tag.strip()

        if not normalized:
            continue

        if not normalized.startswith("#"):
            normalized = f"#{normalized}"

        tags.append(normalized[:80])

    return tags[:12]


def source_key(source):
    lowered = (source or "").lower()

    if "open-meteo" in lowered or "weather api" in lowered:
        return "weather_api"

    if "imd" in lowered:
        return "imd"

    if "citizen" in lowered or "user" in lowered:
        return "citizen"

    if "dataset" in lowered:
        return "public_dataset"

    if "social" in lowered or "hashtag" in lowered:
        return "social_media"

    return lowered or "unknown"


def evaluate_report_signals(
    db: Session,
    source: str,
    description: str,
    confidence_score: float,
    media_urls: list[str],
) -> dict:
    recent_descriptions = [
        item.description
        for item in db.query(WeatherReport.description)
        .order_by(WeatherReport.timestamp.desc())
        .limit(100)
        .all()
        if item.description
    ]

    duplicate = is_duplicate_report(
        description or "",
        recent_descriptions,
    )

    reliability = get_source_reliability(source_key(source))
    confidence = min(max(float(confidence_score or 0.0), 0.0), 1.0)
    trust_score = round(
        min(max((reliability * 0.55) + (confidence * 0.35), 0.0), 1.0),
        2,
    )

    if duplicate["is_duplicate"]:
        trust_score = round(trust_score * 0.65, 2)

    if media_urls:
        trust_score = round(min(trust_score + 0.05, 1.0), 2)

    misinformation_score = round(1.0 - trust_score, 2)

    notes = [
        "Prototype heuristic verification only; no external fact-check authority was queried.",
        f"Source reliability={reliability:.2f}.",
        f"Duplicate similarity={duplicate['similarity']:.2f}.",
        f"Media references={len(media_urls)}.",
    ]

    return {
        "source_reliability": reliability,
        "is_duplicate": duplicate["is_duplicate"],
        "duplicate_similarity": duplicate["similarity"],
        "trust_score": trust_score,
        "misinformation_score": misinformation_score,
        "verification_notes": " ".join(notes),
        "verification_model": "heuristic_prototype",
    }
