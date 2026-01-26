from rules import FieldRule, RulesConfig, apply_rules


def test_apply_regex_rule():
    rules = RulesConfig(fields=[
        FieldRule(name="id", type="regex", pattern=r"ID:(\d+)")
    ])
    result = apply_rules("ID:12345", [], rules, "sample.pdf")
    assert result["id"] == "12345"


def test_apply_keyword_window_rule():
    rules = RulesConfig(fields=[
        FieldRule(
            name="amount",
            type="keyword_window",
            keywords=["Total"],
            window=20,
            pattern=r"(\d+)",
        )
    ])
    result = apply_rules("Total 9000원", [], rules, "sample.pdf")
    assert result["amount"] == "9000"


def test_apply_table_rule():
    tables = [
        [
            ["Item", "Qty", "Amount"],
            ["A", "1", "100"],
            ["B", "2", "200"],
        ]
    ]
    rules = RulesConfig(fields=[
        FieldRule(
            name="last_amount",
            type="table",
            table={"header_match": "Amount", "row_index": -1},
        )
    ])
    result = apply_rules("", tables, rules, "sample.pdf")
    assert result["last_amount"] == "200"
