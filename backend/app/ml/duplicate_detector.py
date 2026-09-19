import re
from difflib import SequenceMatcher


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def calculate_similarity(text1: str, text2: str) -> float:
    normalized_text1 = normalize_text(text1)
    normalized_text2 = normalize_text(text2)

    if not normalized_text1 or not normalized_text2:
        return 0.0

    return round(
        SequenceMatcher(
            None,
            normalized_text1,
            normalized_text2,
        ).ratio(),
        2,
    )


def is_duplicate_report(
    new_description: str,
    existing_descriptions: list[str],
    threshold: float = 0.80,
) -> dict:
    highest_similarity = 0.0

    for existing_description in existing_descriptions:
        similarity = calculate_similarity(
            new_description,
            existing_description,
        )

        highest_similarity = max(
            highest_similarity,
            similarity,
        )

    return {
        "is_duplicate": highest_similarity >= threshold,
        "similarity": highest_similarity,
    }