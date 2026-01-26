import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from text_utils import postprocess_value


@dataclass
class FieldRule:
    name: str
    type: str
    pattern: Optional[str] = None
    keywords: Optional[List[str]] = None
    window: Optional[int] = None
    table: Optional[Dict[str, Any]] = None
    postprocess: Optional[List[str]] = None


@dataclass
class RulesConfig:
    fields: List[FieldRule]


def create_example_rules(path: Path) -> None:
    example = {
        "fields": [
            {
                "name": "invoice_number",
                "type": "regex",
                "pattern": "Invoice\\s*No\\.\\s*([A-Z0-9-]+)",
                "postprocess": ["strip"],
            },
            {
                "name": "total_amount",
                "type": "keyword_window",
                "keywords": ["Total", "합계"],
                "window": 40,
                "pattern": "([0-9,]+\\.?[0-9]{0,2})",
                "postprocess": ["remove_commas", "strip"],
            },
            {
                "name": "issue_date",
                "type": "regex",
                "pattern": "(\\d{4}[.-/]\\d{1,2}[.-/]\\d{1,2})",
                "postprocess": ["date_yyyymmdd"],
            },
            {
                "name": "item_total",
                "type": "table",
                "table": {
                    "header_match": "Amount",
                    "column_index": 3,
                    "row_index": -1,
                },
                "postprocess": ["remove_commas", "strip"],
            },
        ]
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(example, indent=2, ensure_ascii=False), encoding="utf-8")


def load_rules(path: Path) -> RulesConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    fields = [FieldRule(**field) for field in data.get("fields", [])]
    return RulesConfig(fields=fields)


def _apply_regex(text: str, rule: FieldRule) -> Optional[str]:
    if not rule.pattern:
        return None
    match = re.search(rule.pattern, text, re.MULTILINE)
    if not match:
        return None
    if match.groups():
        return match.group(1)
    return match.group(0)


def _apply_keyword_window(text: str, rule: FieldRule) -> Optional[str]:
    if not rule.keywords:
        return None
    window = rule.window or 30
    for keyword in rule.keywords:
        idx = text.find(keyword)
        if idx >= 0:
            start = max(idx - window, 0)
            end = min(idx + window, len(text))
            chunk = text[start:end]
            if rule.pattern:
                match = re.search(rule.pattern, chunk)
                if match:
                    return match.group(1) if match.groups() else match.group(0)
            return chunk
    return None


def _apply_table(tables: List[List[List[str]]], rule: FieldRule) -> Optional[str]:
    if not rule.table:
        return None
    header_match = rule.table.get("header_match")
    column_index = rule.table.get("column_index")
    row_index = rule.table.get("row_index")

    for table in tables:
        if not table:
            continue
        header = table[0]
        column = None
        if header_match and header:
            for idx, cell in enumerate(header):
                if cell and header_match.lower() in cell.lower():
                    column = idx
                    break
        if column is None and isinstance(column_index, int):
            column = column_index

        if column is None:
            continue

        rows = table[1:] if len(table) > 1 else []
        if not rows:
            continue

        row_index_value = 0 if row_index is None else row_index
        if row_index_value < 0:
            row_index_value = len(rows) + row_index_value

        if 0 <= row_index_value < len(rows):
            row = rows[row_index_value]
            if column < len(row):
                return row[column]
    return None


def apply_rules(text: str, tables: List[List[List[str]]], rules: RulesConfig, filename: str) -> Dict[str, Any]:
    record: Dict[str, Any] = {"file": filename}
    for field in rules.fields:
        value = None
        if field.type == "regex":
            value = _apply_regex(text, field)
        elif field.type == "keyword_window":
            value = _apply_keyword_window(text, field)
        elif field.type == "table":
            value = _apply_table(tables, field)

        if value is not None and field.postprocess:
            value = postprocess_value(value, field.postprocess)
        record[field.name] = value
    return record
