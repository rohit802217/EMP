"""
Small, pure validation/normalization helpers.

Kept dependency-free (no streamlit, no pandas) so they can be
unit-tested in isolation.
"""

from config import MAX_MERIT_TOTAL, VALID_ANSWER_OPTIONS_WITH_DELETED


def clean_answer(value):
    """
    Normalize a raw answer value (from OCR or manual entry) into
    a clean uppercase token like 'A', 'B', 'C', 'D', or 'DELETED'.
    Returns the cleaned string as-is if it isn't a recognized option
    (callers can decide how to treat unrecognized values).
    """
    if value is None:
        return ""

    text = str(value).strip().upper().replace(" ", "")

    if text in VALID_ANSWER_OPTIONS_WITH_DELETED:
        return text

    return text


def is_valid_roll_no(roll_no):
    """A roll number is valid if it's non-empty after stripping."""
    return bool(str(roll_no).strip())


def clamp_merit_score(value):
    """
    Coerce a score to a float and clamp it to the valid
    [0, MAX_MERIT_TOTAL] range. Falls back to 0 on bad input.
    """
    try:
        score = float(value)
    except (ValueError, TypeError):
        score = 0.0

    return round(max(0.0, min(MAX_MERIT_TOTAL, score)), 2)
