import re


EVENT_KEYWORDS = {
    "rainfall": [
        "rain",
        "rainfall",
        "raining",
        "heavy rain",
        "downpour",
        "precipitation",
    ],
    "thunderstorm": [
        "thunderstorm",
        "thunder",
        "lightning",
        "storm",
    ],
    "flooding": [
        "flood",
        "flooding",
        "waterlogging",
        "water logged",
        "inundation",
    ],
    "heatwave": [
        "heatwave",
        "heat wave",
        "extreme heat",
        "very hot",
        "high temperature",
    ],
    "fog": [
        "fog",
        "dense fog",
        "mist",
        "low visibility",
    ],
    "dust_storm": [
        "dust storm",
        "duststorm",
        "dust cloud",
    ],
    "strong_winds": [
        "strong wind",
        "high wind",
        "gust",
        "gusty wind",
        "storm winds",
    ],
}


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def classify_weather_event(text: str) -> dict:
    normalized_text = normalize_text(text)

    scores = {}

    for event_type, keywords in EVENT_KEYWORDS.items():
        score = 0

        for keyword in keywords:
            if keyword in normalized_text:
                score += 1

        scores[event_type] = score

    detected_event = max(
        scores,
        key=scores.get,
    )

    detected_score = scores[detected_event]

    if detected_score == 0:
        return {
            "event_type": "unknown",
            "confidence": 0.0,
        }

    confidence = min(
        0.5 + (detected_score * 0.15),
        0.95,
    )

    return {
        "event_type": detected_event,
        "confidence": round(confidence, 2),
    }