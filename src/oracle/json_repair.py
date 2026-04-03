"""Robust JSON parsing for LLM-generated responses.

LLMs frequently produce malformed JSON, especially when generating long
content with markdown formatting inside string values. This module provides
repair strategies to recover valid JSON from common failure modes:

1. Literal newlines inside string values (most common)
2. Markdown code fences wrapping the JSON
3. Trailing commas in arrays/objects
4. Single quotes instead of double quotes
5. Truncated JSON (incomplete responses)
6. Unescaped control characters in strings
7. Extra text before/after the JSON array
"""

from __future__ import annotations

import json
import logging
import re

logger = logging.getLogger(__name__)


def parse_llm_json(text: str) -> list | None:
    """Parse LLM-generated JSON with multiple repair strategies.

    Args:
        text: Raw LLM response text.

    Returns:
        List of parsed items (usually dicts, but may be strings for
        array-of-strings responses like paraphrases), or None if all
        repair attempts fail.
    """
    cleaned = _strip_fences(text.strip())

    # Strategy 1: Direct parse (fast path)
    result = _try_parse(cleaned)
    if result is not None:
        return result

    # Strategy 2: Fix literal newlines inside strings
    fixed = _fix_literal_newlines(cleaned)
    result = _try_parse(fixed)
    if result is not None:
        logger.debug("JSON repaired by fixing literal newlines")
        return result

    # Strategy 3: Extract JSON array from surrounding text
    extracted = _extract_json_array(cleaned)
    if extracted:
        result = _try_parse(extracted)
        if result is not None:
            logger.debug("JSON repaired by extracting array from text")
            return result

        # Also try newline fix on extracted
        fixed = _fix_literal_newlines(extracted)
        result = _try_parse(fixed)
        if result is not None:
            logger.debug("JSON repaired by extracting + fixing newlines")
            return result

    # Strategy 4: Fix trailing commas
    fixed = _fix_trailing_commas(cleaned)
    result = _try_parse(fixed)
    if result is not None:
        logger.debug("JSON repaired by fixing trailing commas")
        return result

    # Strategy 5: Fix truncated JSON (close unclosed brackets)
    fixed = _fix_truncated(cleaned)
    result = _try_parse(fixed)
    if result is not None:
        logger.debug("JSON repaired by closing truncated brackets")
        return result

    # Strategy 6: Combined — newlines + trailing commas + truncation
    fixed = _fix_literal_newlines(cleaned)
    fixed = _fix_trailing_commas(fixed)
    fixed = _fix_truncated(fixed)
    result = _try_parse(fixed)
    if result is not None:
        logger.debug("JSON repaired by combined fixes")
        return result

    # Strategy 7: Try parsing individual objects separated by newlines
    result = _parse_ndjson(cleaned)
    if result is not None:
        logger.debug("JSON repaired by parsing as NDJSON")
        return result

    # Strategy 8: Nuclear — regex-based key-value extraction
    # Handles the worst case: newlines + unescaped quotes + truncation
    result = _regex_extract_objects(cleaned)
    if result is not None:
        logger.debug("JSON repaired by regex key-value extraction")
        return result

    # All strategies failed
    return None


def _strip_fences(text: str) -> str:
    """Remove markdown code fences, thinking tags, and other LLM wrappers."""
    # Remove <think>...</think> blocks (Nemotron, DeepSeek, Qwen, etc.)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # Also handle unclosed <think> (model still "thinking" when it started outputting)
    text = re.sub(r"<think>.*", "", text, flags=re.DOTALL)

    if text.startswith("```"):
        # Remove opening fence (with optional language tag)
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        # Remove closing fence
        text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def _try_parse(text: str) -> list[dict] | None:
    """Attempt JSON parse, return list of dicts or None."""
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        return None
    except (json.JSONDecodeError, ValueError):
        return None


def _fix_literal_newlines(text: str) -> str:
    """Escape literal newlines that appear inside JSON string values.

    This is the most common LLM JSON error: the model outputs multi-line
    content (especially markdown) inside JSON strings without escaping the
    newlines. We need to find newlines that are inside quoted strings and
    replace them with \\n.
    """
    result = []
    in_string = False
    escape_next = False
    i = 0

    while i < len(text):
        char = text[i]

        if escape_next:
            result.append(char)
            escape_next = False
            i += 1
            continue

        if char == "\\":
            result.append(char)
            escape_next = True
            i += 1
            continue

        if char == '"':
            in_string = not in_string
            result.append(char)
            i += 1
            continue

        if in_string:
            if char == "\n":
                result.append("\\n")
            elif char == "\r":
                result.append("\\r")
            elif char == "\t":
                result.append("\\t")
            else:
                result.append(char)
        else:
            result.append(char)

        i += 1

    return "".join(result)


def _fix_trailing_commas(text: str) -> str:
    """Remove trailing commas before closing brackets."""
    # Remove trailing comma before ] or }
    text = re.sub(r",\s*([\]\}])", r"\1", text)
    return text


def _fix_truncated(text: str) -> str:
    """Attempt to close unclosed JSON brackets/braces.

    If the LLM response was truncated, we may have unclosed strings,
    objects, or arrays. Try to close them to recover what we can.
    """
    # Count unclosed brackets
    open_brackets = 0
    open_braces = 0
    in_string = False
    escape_next = False

    for char in text:
        if escape_next:
            escape_next = False
            continue
        if char == "\\":
            escape_next = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "[":
            open_brackets += 1
        elif char == "]":
            open_brackets -= 1
        elif char == "{":
            open_braces += 1
        elif char == "}":
            open_braces -= 1

    if in_string:
        # Close the unclosed string
        text += '"'

    # Close unclosed braces and brackets
    if open_braces > 0 or open_brackets > 0:
        # Remove any trailing incomplete key-value pair or comma
        text = re.sub(r',\s*"[^"]*"?\s*:?\s*$', "", text)
        text = re.sub(r",\s*$", "", text)

        text += "}" * max(0, open_braces)
        text += "]" * max(0, open_brackets)

    return text


def _extract_json_array(text: str) -> str | None:
    """Find and extract a JSON array from text that may have extra content."""
    # Find the first [ and the last ]
    first_bracket = text.find("[")
    last_bracket = text.rfind("]")

    if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
        return text[first_bracket : last_bracket + 1]

    # Try finding a JSON object instead
    first_brace = text.find("{")
    last_brace = text.rfind("}")

    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return text[first_brace : last_brace + 1]

    return None


def _parse_ndjson(text: str) -> list[dict] | None:
    """Try parsing as newline-delimited JSON objects.

    Tracks string state to avoid being confused by braces inside
    string values (e.g., zone file examples, JSON snippets in answers).
    """
    results = []
    depth = 0
    start = None
    in_string = False
    escape_next = False

    for i, char in enumerate(text):
        if escape_next:
            escape_next = False
            continue
        if char == "\\" and in_string:
            escape_next = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue

        if char == "{":
            if depth == 0:
                start = i
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0 and start is not None:
                fragment = text[start : i + 1]
                try:
                    obj = json.loads(fragment)
                    if isinstance(obj, dict):
                        results.append(obj)
                except json.JSONDecodeError:
                    # Try with newline fix
                    fixed = _fix_literal_newlines(fragment)
                    try:
                        obj = json.loads(fixed)
                        if isinstance(obj, dict):
                            results.append(obj)
                    except json.JSONDecodeError:
                        pass
                start = None

    return results if results else None


def _regex_extract_objects(text: str) -> list[dict] | None:
    """Nuclear option: extract key-value pairs using regex patterns.

    When all other strategies fail (usually due to unescaped quotes inside
    string values combined with newlines and truncation), this function
    uses regex to find JSON keys and extract the content between them.

    This is lossy — it may mangle some values — but it recovers something
    rather than losing the entire LLM response.
    """
    # Find all JSON key patterns: "key_name":
    key_pattern = re.compile(r'"(\w+)"\s*:\s*')

    # Find the boundaries of each object (look for { at depth 0)
    objects: list[dict] = []

    # Split on object boundaries heuristically
    # Look for lines that start a new key after a potential object boundary
    # Strategy: find all "key": "value" pairs using a greedy approach

    # First, find all key positions
    key_matches = list(key_pattern.finditer(text))
    if not key_matches:
        return None

    current_obj: dict = {}

    for i, match in enumerate(key_matches):
        key = match.group(1)
        value_start = match.end()

        # Determine where the value ends
        if i + 1 < len(key_matches):
            # Value ends before the next key (minus the comma and whitespace)
            next_key_start = key_matches[i + 1].start()
            raw_value = text[value_start:next_key_start].strip()
        else:
            # Last key — take everything to the end
            raw_value = text[value_start:].strip()

        # Clean up the raw value
        # Remove trailing commas, brackets, braces
        raw_value = raw_value.rstrip().rstrip(",").rstrip()
        raw_value = re.sub(r'[\}\]]\s*,?\s*$', '', raw_value).strip()

        # Try to parse the value as JSON first
        parsed_value = None
        for attempt in [raw_value, raw_value + '"', '"' + raw_value + '"']:
            try:
                parsed_value = json.loads(attempt)
                break
            except (json.JSONDecodeError, ValueError):
                continue

        if parsed_value is None:
            # Extract string content between quotes, handling newlines
            string_match = re.match(r'^"(.*)', raw_value, re.DOTALL)
            if string_match:
                content = string_match.group(1)
                # Remove trailing quote if present
                if content.endswith('"'):
                    content = content[:-1]
                # Escape any remaining problematic characters
                content = content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                parsed_value = content
            elif raw_value.startswith('['):
                # Try to parse as array, closing if truncated
                attempt = raw_value
                if not attempt.endswith(']'):
                    attempt = re.sub(r',\s*$', '', attempt) + ']'
                try:
                    parsed_value = json.loads(attempt)
                except (json.JSONDecodeError, ValueError):
                    # Last resort: extract strings from array-like content
                    items = re.findall(r'"([^"]*)"', raw_value)
                    parsed_value = items if items else raw_value
            else:
                parsed_value = raw_value.strip('"')

        # Detect object boundaries
        # If we see the same key again or hit a `{`, start a new object
        if key in current_obj and current_obj:
            objects.append(current_obj)
            current_obj = {}

        current_obj[key] = parsed_value

    # Don't forget the last object
    if current_obj:
        # Only add if it has at least a question/answer or user_question
        has_content = any(
            k in current_obj
            for k in ("question", "answer", "user_question", "scenario", "analysis", "turns")
        )
        if has_content:
            objects.append(current_obj)

    return objects if objects else None
