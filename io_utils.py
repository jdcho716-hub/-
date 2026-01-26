import csv
import json
from pathlib import Path
from typing import Any, Dict, List


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_results_json(path: Path, records: List[Dict[str, Any]]) -> None:
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")


def save_results_csv(path: Path, records: List[Dict[str, Any]]) -> None:
    if not records:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(records[0].keys())
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def save_errors_csv(path: Path, errors: List[Dict[str, Any]]) -> None:
    if not errors:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = ["file", "reason", "stack"]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(errors)
