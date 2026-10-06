import pytest

from utils.json_parser import parse_json_from_response


def test_parse_direct_json():
    raw = '{"patch_code": "fixed bug in parser", "relevant_files": ["parser.py"]}'
    parsed = parse_json_from_response(raw)
    assert parsed["patch_code"] == "fixed bug in parser"
    assert parsed["relevant_files"] == ["parser.py"]


def test_parse_markdown_fenced_json():
    raw = """Here is the resulting plan:
```json
{
    "fix_plan": "1. Add null check",
    "relevant_files": ["src/parser.py"]
}
```
Hope this helps!"""
    parsed = parse_json_from_response(raw)
    assert parsed["fix_plan"] == "1. Add null check"
    assert parsed["relevant_files"] == ["src/parser.py"]


def test_parse_embedded_braces():
    raw = "The final verdict is {\"status\": \"SUCCESS\", \"retry_count\": 0}. Done."
    parsed = parse_json_from_response(raw)
    assert parsed["status"] == "SUCCESS"
    assert parsed["retry_count"] == 0


def test_parse_invalid_raises():
    with pytest.raises(ValueError):
        parse_json_from_response("No json here at all.")
