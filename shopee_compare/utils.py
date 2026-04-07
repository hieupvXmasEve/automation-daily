from __future__ import annotations

from datetime import datetime
import math
import re
import unicodedata
from typing import Iterable


WHITESPACE_RE = re.compile(r"\s+")


def is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    text = str(value).strip()
    return text == "" or text.lower() == "nan"


def normalize_text(value: object) -> str | None:
    if is_missing(value):
        return None
    return WHITESPACE_RE.sub(" ", str(value)).strip()


def normalize_lines(value: object) -> list[str]:
    if is_missing(value):
        return []
    lines: list[str] = []
    for raw_line in str(value).splitlines():
        line = normalize_text(raw_line)
        if line:
            lines.append(line)
    return lines


def first_non_empty(values: Iterable[object]) -> str | None:
    for value in values:
        text = normalize_text(value)
        if text:
            return text
    return None


def parse_int(value: object) -> int | None:
    if is_missing(value):
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value))
    text = str(value).strip().replace(",", "").replace(".0", "")
    digits = re.sub(r"[^\d-]", "", text)
    if digits in {"", "-"}:
        return None
    return int(digits)


def parse_float(value: object) -> float | None:
    if is_missing(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    return float(match.group(0))


def iso_datetime(value: object) -> str | None:
    if is_missing(value):
        return None
    if hasattr(value, "to_pydatetime"):
        value = value.to_pydatetime()
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    text = str(value).strip()
    for fmt in (
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d-%m-%Y %H:%M",
        "%d-%m-%Y",
    ):
        try:
            dt = datetime.strptime(text, fmt)
            if "H" in fmt:
                return dt.strftime("%Y-%m-%d %H:%M")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return normalize_text(text)


def parse_pdf_datetime(date_text: str | None, time_text: str | None) -> str | None:
    if not date_text:
        return None
    candidate = date_text if not time_text else f"{date_text} {time_text}"
    return iso_datetime(candidate)


def bool_label(value: bool | None) -> str:
    if value is None:
        return ""
    return "yes" if value else "no"


def safe_compare(left: object, right: object) -> bool | None:
    left_text = normalize_text(left)
    right_text = normalize_text(right)
    if not left_text or not right_text:
        return None
    return left_text == right_text


def join_notes(notes: list[str]) -> str:
    if not notes:
        return ""
    return "; ".join(dict.fromkeys(notes))


def slugify_text(value: object) -> str:
    text = normalize_text(value) or ""
    normalized = unicodedata.normalize("NFKD", text)
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return "".join(ch.lower() for ch in without_accents if ch.isalnum())


def ascii_fold_text(value: object) -> str:
    text = normalize_text(value) or ""
    normalized = unicodedata.normalize("NFKD", text)
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return without_accents.lower()


def text_tokens(value: object) -> list[str]:
    return re.findall(r"[a-z0-9]+", ascii_fold_text(value))


def token_set_with_adjacent(value: object) -> set[str]:
    tokens = text_tokens(value)
    merged = set(tokens)
    for left, right in zip(tokens, tokens[1:]):
        merged.add(left + right)
    return merged
