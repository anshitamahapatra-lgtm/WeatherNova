SOURCE_RELIABILITY = {
    "imd": 0.95,
    "government": 0.90,
    "weather_api": 0.85,
    "public_dataset": 0.80,
    "news": 0.70,
    "citizen": 0.60,
    "social_media": 0.40,
    "unknown": 0.30,
}


def get_source_reliability(source: str) -> float:
    normalized_source = source.lower().strip()

    return SOURCE_RELIABILITY.get(
        normalized_source,
        SOURCE_RELIABILITY["unknown"],
    )


def calculate_trust_score(
    source: str,
    classification_confidence: float,
    is_duplicate: bool,
) -> float:
    source_score = get_source_reliability(source)

    trust_score = (
        source_score * 0.50
        + classification_confidence * 0.30
    )

    if is_duplicate:
        trust_score *= 0.50

    return round(
        min(max(trust_score, 0.0), 1.0),
        2,
    )