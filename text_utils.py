import re
from typing import List, Optional


WHITESPACE_RE = re.compile(r"\s+")
DATE_RE = re.compile(r"(\d{4})[./-](\d{1,2})[./-](\d{1,2})")


def normalize_text(text: str) -> str:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = cleaned.replace("\u00a0", " ")
    cleaned = WHITESPACE_RE.sub(" ", cleaned)
    return cleaned.strip()


def parse_pages(pages_spec: str) -> List[int]:
    pages: List[int] = []
    for part in pages_spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            start = int(start_str)
            end = int(end_str)
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))
    return sorted(set(pages))


def postprocess_value(value: str, steps: List[str]) -> str:
    result = value
    for step in steps:
        if step == "strip":
            result = result.strip()
        elif step == "digits_only":
            result = re.sub(r"\D", "", result)
        elif step == "remove_commas":
            result = result.replace(",", "")
        elif step == "date_yyyymmdd":
            match = DATE_RE.search(result)
            if match:
                year, month, day = match.groups()
                result = f"{int(year):04d}{int(month):02d}{int(day):02d}"
    return result
