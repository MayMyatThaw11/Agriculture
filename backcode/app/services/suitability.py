"""Pure crop suitability entry point used by the assessment service."""

from app.domain import assess


def score_crop(values: dict, requirements: dict | None = None) -> dict:
    return assess(values, requirements)
