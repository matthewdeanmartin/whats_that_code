"""
Parsing-based language detection.

Only works for Python, JSON, and XML where lightweight parsers are available.
"""

import ast
import json

import defusedxml.ElementTree


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


def parses_as_xml(code: str) -> bool:
    """If it parses as xml, it probably is xml or something like it"""
    if "<" not in code or ">" not in code:
        return False
    try:
        defusedxml.ElementTree.fromstring(code, forbid_dtd=True)
        return True
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
    return guesses
