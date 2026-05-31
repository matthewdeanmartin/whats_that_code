"""
Parsing-based language detection.

Only works for Python, JSON, and XML where lightweight parsers are available.
"""

import ast
import json

from lxml import etree as _lxml_etree

try:  # stdlib on 3.11+, absent on 3.10 (the project supports >=3.10)
    import tomllib as _tomllib
except ModuleNotFoundError:  # pragma: no cover - only on 3.10
    _tomllib = None  # type: ignore[assignment]


def parses_as_python(code: str) -> bool:
    """Validate by ast parsing"""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def parses_as_json(code: str) -> bool:
    """Validate by json.loads"""
    try:
        json.loads(code)
        return True
    except Exception:  # pylint: disable=broad-exception-caught
        return False


_XHTML_NS = "http://www.w3.org/1999/xhtml"


def _is_html_root(root) -> bool:
    """Return True if the XML root element indicates an HTML/XHTML document."""
    tag = root.tag
    # lxml uses Clark notation: {namespace}localname
    if isinstance(tag, str):
        if tag == "html" or tag.lower() == "html":
            return True
        if tag == f"{{{_XHTML_NS}}}html":
            return True
    return False


def parses_as_xml(code: str) -> bool:
    """If it parses as xml, it probably is xml or something like it.

    Returns False when the root element is ``<html>`` (including XHTML), so
    that well-formed XHTML files are not misidentified as generic XML.
    """
    if "<" not in code or ">" not in code:
        return False
    try:
        parser = _lxml_etree.XMLParser(resolve_entities=False, no_network=True)
        root = _lxml_etree.fromstring(code.encode(), parser)
        return not _is_html_root(root)
    except Exception:  # pylint: disable=broad-exception-caught
        return False


def parses_as_toml(code: str) -> bool:
    """Validate by tomllib (3.11+). Always False on 3.10 (no tomllib).

    Guarded so a bare ``key = value`` or single ``[section]`` does not count —
    those parse as TOML but are too weak a signal to be useful.
    """
    if _tomllib is None or "=" not in code:
        return False
    try:
        parsed = _tomllib.loads(code)
        return bool(parsed)
    except Exception:  # pylint: disable=broad-exception-caught
        return False


def language_by_parsing(code: str) -> list[str]:
    """Guess by parsing"""
    if not code or not code.strip():
        return []
    guesses = []
    if parses_as_python(code):
        guesses.append("python")
    if parses_as_json(code):
        guesses.append("json")
    if parses_as_xml(code):
        guesses.append("xml")
    if parses_as_toml(code):
        guesses.append("toml")
    return guesses
