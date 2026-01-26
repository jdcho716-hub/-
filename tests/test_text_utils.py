import pytest

from text_utils import normalize_text, parse_pages, postprocess_value


def test_normalize_text_collapses_whitespace():
    text = "Hello\r\nWorld\t  Test"
    assert normalize_text(text) == "Hello World Test"


def test_parse_pages_ranges_and_single():
    assert parse_pages("1-3,5") == [1, 2, 3, 5]


def test_postprocess_digits_only():
    assert postprocess_value("A-12,300원", ["digits_only"]) == "12300"


def test_postprocess_date_yyyymmdd():
    assert postprocess_value("2024/1/5", ["date_yyyymmdd"]) == "20240105"
