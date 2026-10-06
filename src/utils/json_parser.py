"""
Robust JSON extractor for LLM responses.
Handles raw JSON, markdown-fenced blocks, and conversational preamble/postscript.
"""

import json
import re
from typing import Any


def parse_json_from_response(content: Any) -> dict[str, Any]:
    """Extract and parse a JSON dictionary from LLM string output."""
    if not isinstance(content, str):
        content = str(content)

    text = content.strip()

    # 1. Direct parse attempt
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, ValueError):
        pass

    # 2. Extract from markdown code fences: ```json ... ``` or ``` ... ```
    fence_pattern = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
    matches = fence_pattern.findall(text)
    for match in matches:
        try:
            data = json.loads(match.strip())
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, ValueError):
            continue

    # 3. Extract outermost curly braces: { ... }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = text[first_brace : last_brace + 1]
        try:
            data = json.loads(candidate.strip())
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, ValueError):
            pass

    raise ValueError(f"Could not parse valid JSON object from LLM response:\n{text[:500]}")
