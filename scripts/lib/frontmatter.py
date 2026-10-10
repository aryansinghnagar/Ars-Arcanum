#!/usr/bin/env python3
"""
Ars Arcanum Unified YAML Frontmatter Engine (scripts/lib/frontmatter.py)
=======================================================================
High-performance, pure-Python standard library YAML frontmatter parser and extractor.
Provides safe, zero-dependency recursive parsing of YAML frontmatter headers,
nested dictionaries, lists of dictionaries, block scalars, and metadata across
all World Bibles, world vaults, and manuscript files.
"""

from __future__ import annotations

import json
import re
from typing import Any

FRONTMATTER_DELIM = "---"
FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)


def _coerce_scalar(val: str) -> Any:
    """Coerces a string scalar to int, float, bool, null, or unquoted string."""
    stripped = val.strip()
    if not stripped:
        return ""

    # Quoted strings
    if (stripped.startswith('"') and stripped.endswith('"')) or (stripped.startswith("'") and stripped.endswith("'")):
        inner = stripped[1:-1]
        # Unescape standard double quote escapes if double-quoted
        if stripped.startswith('"'):
            inner = inner.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t').replace('\\\\', '\\')
        return inner

    lower = stripped.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    if lower in ("none", "null", "~"):
        return None

    # Integer (including signed)
    if re.match(r"^[+-]?\d+$", stripped):
        try:
            return int(stripped)
        except ValueError:
            pass

    # Float (including scientific notation)
    if re.match(r"^[+-]?\d+\.\d+$", stripped) or re.match(r"^[+-]?\d+(?:\.\d+)?[eE][+-]?\d+$", stripped):
        try:
            return float(stripped)
        except ValueError:
            pass

    # Inline List [a, b, c]
    if stripped.startswith("[") and stripped.endswith("]"):
        inner = stripped[1:-1].strip()
        if not inner:
            return []
        items = []
        for part in _split_comma_preserving_quotes(inner):
            items.append(_coerce_scalar(part.strip()))
        return items

    # Inline Dict {a: 1, b: 2}
    if stripped.startswith("{") and stripped.endswith("}"):
        inner = stripped[1:-1].strip()
        if not inner:
            return {}
        d: dict[str, Any] = {}
        for part in _split_comma_preserving_quotes(inner):
            if ":" in part:
                k, v = part.split(":", 1)
                d[k.strip().strip("\"'")] = _coerce_scalar(v.strip())
        return d

    return stripped


def _split_comma_preserving_quotes(text: str) -> list[str]:
    """Splits a comma-delimited string while respecting nested quotes, brackets, and braces."""
    parts = []
    current: list[str] = []
    in_single = False
    in_double = False
    depth = 0

    for ch in text:
        if ch == "'" and not in_double:
            in_single = not in_single
            current.append(ch)
        elif ch == '"' and not in_single:
            in_double = not in_double
            current.append(ch)
        elif ch in ("[", "{") and not in_single and not in_double:
            depth += 1
            current.append(ch)
        elif ch in ("]", "}") and not in_single and not in_double:
            depth = max(0, depth - 1)
            current.append(ch)
        elif ch == "," and not in_single and not in_double and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)

    if current:
        parts.append("".join(current))
    return [p.strip() for p in parts if p.strip()]


def _parse_yaml_recursive(lines: list[str], start_idx: int = 0, base_indent: int = 0) -> tuple[Any, int]:
    """
    Recursively parses indented YAML lines starting at start_idx into dicts, lists, or scalars.
    Returns (parsed_structure, next_line_index).
    """
    n = len(lines)
    i = start_idx

    # Determine whether current block is a list or dict
    # Peek at first non-empty, non-comment line
    is_list_block = False
    while i < n:
        raw = lines[i]
        stripped = raw.strip()
        if stripped and not stripped.startswith("#"):
            indent = len(raw) - len(raw.lstrip(" "))
            if indent < base_indent:
                # Lower indent -> return empty
                return {}, i
            if stripped.startswith("- ") or stripped == "-":
                is_list_block = True
            break
        i += 1

    if i >= n:
        return {}, n

    if is_list_block:
        result_list: list[Any] = []
        while i < n:
            raw = lines[i]
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                i += 1
                continue

            indent = len(raw) - len(raw.lstrip(" "))
            if indent < base_indent:
                break

            if stripped.startswith("- ") or stripped == "-":
                item_content = stripped[2:].strip() if stripped.startswith("- ") else ""
                child_indent = indent + 2

                is_quoted = (item_content.startswith('"') and item_content.endswith('"')) or (item_content.startswith("'") and item_content.endswith("'"))
                is_mapping = not is_quoted and ":" in item_content and not item_content.startswith(("[", "{"))

                # Check if item is an unquoted key-value mapping on same line (e.g. "- name: Gold")
                if is_mapping:
                    # Start dict for this list item
                    k, v = item_content.split(":", 1)
                    k = k.strip().strip("\"'")
                    v = v.strip()
                    sub_dict: dict[str, Any] = {}
                    if v:
                        sub_dict[k] = _coerce_scalar(v)
                    else:
                        sub_val, sub_next = _parse_yaml_recursive(lines, i + 1, child_indent)
                        sub_dict[k] = sub_val
                        i = sub_next
                        result_list.append(sub_dict)
                        continue

                    # Consume further keys for this list item at child_indent
                    i += 1
                    while i < n:
                        next_raw = lines[i]
                        next_strip = next_raw.strip()
                        if not next_strip or next_strip.startswith("#"):
                            i += 1
                            continue
                        next_indent = len(next_raw) - len(next_raw.lstrip(" "))
                        if next_indent < child_indent or next_strip.startswith("- "):
                            break
                        if ":" in next_strip:
                            nk, nv = next_strip.split(":", 1)
                            nk = nk.strip().strip("\"'")
                            nv = nv.strip()
                            if nv:
                                sub_dict[nk] = _coerce_scalar(nv)
                                i += 1
                            else:
                                n_val, n_next = _parse_yaml_recursive(lines, i + 1, next_indent + 2)
                                sub_dict[nk] = n_val
                                i = n_next
                        else:
                            i += 1
                    result_list.append(sub_dict)
                    continue

                if item_content:
                    result_list.append(_coerce_scalar(item_content))
                    i += 1
                else:
                    # Item content is indented on next lines
                    sub_val, sub_next = _parse_yaml_recursive(lines, i + 1, child_indent)
                    result_list.append(sub_val)
                    i = sub_next
            else:
                # Unexpected line at list level
                break
        return result_list, i

    # Dictionary block
    result_dict: dict[str, Any] = {}
    while i < n:
        raw = lines[i]
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        indent = len(raw) - len(raw.lstrip(" "))
        if indent < base_indent:
            break

        # Handle list item encountered inside dictionary (e.g. root dash or loose list)
        if stripped.startswith("- ") or stripped == "-":
            # If current dict is empty, convert/delegate to list
            if not result_dict:
                sub_list, sub_next = _parse_yaml_recursive(lines, i, indent)
                return sub_list, sub_next
            i += 1
            continue

        if ":" in stripped:
            key, val = stripped.split(":", 1)
            key = key.strip().strip("\"'")
            val = val.strip()

            if val in ("|", "|-", "|+", ">", ">-", ">+"):
                # Multi-line block scalar
                scalar_lines = []
                block_indent = None
                is_folded = val.startswith(">")
                i += 1
                while i < n:
                    b_raw = lines[i]
                    b_strip = b_raw.strip()
                    if not b_strip:
                        scalar_lines.append("")
                        i += 1
                        continue
                    b_indent = len(b_raw) - len(b_raw.lstrip(" "))
                    if block_indent is None:
                        if b_indent <= indent:
                            break
                        block_indent = b_indent
                    elif b_indent < block_indent:
                        break
                    scalar_lines.append(b_raw[block_indent:] if len(b_raw) >= block_indent else b_strip)
                    i += 1
                if is_folded:
                    result_dict[key] = " ".join(scalar_lines).strip()
                else:
                    result_dict[key] = "\n".join(scalar_lines).strip()
                continue

            if val:
                result_dict[key] = _coerce_scalar(val)
                i += 1
            else:
                # Key with empty value -> check if followed by nested block or list
                sub_indent = indent + 1
                if i + 1 < n:
                    peek_raw = lines[i + 1]
                    peek_strip = peek_raw.strip()
                    if peek_strip and not peek_strip.startswith("#"):
                        peek_indent = len(peek_raw) - len(peek_raw.lstrip(" "))
                        if peek_strip.startswith("- "):
                            sub_indent = min(indent, peek_indent)
                        elif peek_indent > indent:
                            sub_indent = peek_indent
                sub_val, sub_next = _parse_yaml_recursive(lines, i + 1, sub_indent)
                result_dict[key] = sub_val if (sub_val != {} or sub_next > i + 1) else ""
                i = sub_next
        else:
            i += 1

    return result_dict, i


def _parse_yaml_lines(lines: list[str]) -> dict[str, Any]:
    """Parses a list of YAML lines into a dictionary, supporting nested structures and lists."""
    res, _ = _parse_yaml_recursive(lines, 0, 0)
    if isinstance(res, dict):
        return res
    if isinstance(res, list):
        return {"items": res}
    return {}


def parse_yaml_frontmatter(content: str) -> dict[str, Any]:
    """
    Parses YAML frontmatter block from Markdown content into a dictionary.
    Supports key-value pairs, nested dictionaries, inline lists ([a, b]),
    bulleted lists (- item), lists of objects, block scalars, and scalar coercion.
    Returns an empty dict if no valid frontmatter is found.
    """
    fm_match = FRONTMATTER_REGEX.match(content)
    if not fm_match:
        return {}

    lines = fm_match.group(1).splitlines()
    return _parse_yaml_lines(lines)


def parse_yaml_document(content: str) -> dict[str, Any]:
    """
    Parses a YAML document (such as manuscript.yaml or world.yaml) or frontmatter block.
    """
    fm_match = FRONTMATTER_REGEX.match(content)
    if fm_match:
        return parse_yaml_frontmatter(content)

    lines = content.splitlines()
    if lines and lines[0].strip() == FRONTMATTER_DELIM:
        lines = lines[1:]
    if lines and lines[-1].strip() == FRONTMATTER_DELIM:
        lines = lines[:-1]

    return _parse_yaml_lines(lines)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], bool]:
    """
    Strict subset parser returning (frontmatter_dict, success_boolean).
    Used by world_doctor for structural verification.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return {}, True

    # Scan for closing delimiter
    closing_idx = -1
    for idx in range(1, len(lines)):
        if lines[idx].strip() == FRONTMATTER_DELIM:
            closing_idx = idx
            break

    if closing_idx == -1:
        # Unclosed frontmatter
        return {}, False

    fm_lines = lines[1:closing_idx]

    # Validate syntax of each line before full parse
    for raw in fm_lines:
        s = raw.strip()
        if not s or s.startswith(("#", "- ")):
            continue
        if ":" not in s:
            return {}, False

    try:
        fm = _parse_yaml_lines(fm_lines)
        return fm, True
    except Exception:
        return {}, False


def _serialize_scalar(val: Any) -> str:
    """Serializes a Python scalar into a standard YAML representation."""
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return str(val)
    s = str(val)
    if not s:
        return '""'
    # Check if quotes are required
    if any(c in s for c in (':', '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@', '\\', '"', "'", '\n')):
        escaped = s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        return f'"{escaped}"'
    # Numeric lookalikes or boolean strings should be quoted
    if s.lower() in ("true", "false", "yes", "no", "null", "none", "~") or re.match(r"^[+-]?\d+(?:\.\d+)?$", s):
        return f'"{s}"'
    return s


def serialize_yaml_document(data: dict[str, Any], indent: int = 0) -> str:
    """Serializes a Python dictionary into a pure YAML document."""
    lines: list[str] = []
    prefix = "  " * indent

    for key, val in data.items():
        k_str = str(key)
        if isinstance(val, dict):
            if not val:
                lines.append(f"{prefix}{k_str}: {{}}")
            else:
                lines.append(f"{prefix}{k_str}:")
                nested = serialize_yaml_document(val, indent=indent + 1)
                lines.append(nested)
        elif isinstance(val, list):
            if not val:
                lines.append(f"{prefix}{k_str}: []")
            else:
                lines.append(f"{prefix}{k_str}:")
                for item in val:
                    if isinstance(item, dict):
                        # First key of dict on same line as hyphen
                        dict_lines = serialize_yaml_document(item, indent=indent + 2).splitlines()
                        if dict_lines:
                            first = dict_lines[0].lstrip()
                            lines.append(f"{prefix}  - {first}")
                            for rem in dict_lines[1:]:
                                lines.append(rem)
                        else:
                            lines.append(f"{prefix}  - {{}}")
                    elif isinstance(item, list):
                        lines.append(f"{prefix}  - {json.dumps(item)}")
                    else:
                        lines.append(f"{prefix}  - {_serialize_scalar(item)}")
        else:
            lines.append(f"{prefix}{k_str}: {_serialize_scalar(val)}")

    return "\n".join(lines)


def serialize_yaml_frontmatter(data: dict[str, Any], body: str = "") -> str:
    """Serializes metadata into fenced YAML frontmatter with markdown body."""
    yaml_str = serialize_yaml_document(data)
    if body:
        return f"---\n{yaml_str}\n---\n\n{body.lstrip()}"
    return f"---\n{yaml_str}\n---\n"


dump_frontmatter = serialize_yaml_frontmatter


def extract_frontmatter_and_body(content: str) -> tuple[dict[str, Any], str]:
    """Splits markdown content into frontmatter metadata dictionary and body text."""
    fm_match = FRONTMATTER_REGEX.match(content)
    if not fm_match:
        return {}, content

    fm_dict = parse_yaml_frontmatter(content)
    body = content[fm_match.end():]
    return fm_dict, body


__all__ = [
    "FRONTMATTER_DELIM",
    "FRONTMATTER_REGEX",
    "_coerce_scalar",
    "_parse_yaml_lines",
    "_serialize_scalar",
    "dump_frontmatter",
    "extract_frontmatter_and_body",
    "parse_frontmatter",
    "parse_yaml_document",
    "parse_yaml_frontmatter",
    "serialize_yaml_document",
    "serialize_yaml_frontmatter",
]

