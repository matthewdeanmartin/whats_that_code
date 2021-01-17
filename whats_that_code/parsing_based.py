"""
This only works for python and certain languages where there are easy to find parsers.

I figure these are likely to be slow & explode the number of libs installed.

TODO:
c parser - pip install pycparser
java parser - pip install plp.Java (abandoned?)
php parser = pip install convert2php (maybe?)
javascript parser = pip install pyesprima
html = pip install py_w3c (html can be pretty bad and still 'parse')
"""
import ast
import json
from typing import List

import defusedxml.ElementTree


def parses_as_python(code: str) -> bool:
    """Validate by ast parsing"""
    try:
        _ = ast.parse(code)
        return True
    except SyntaxError:
        return False


def parses_as_json(code: str) -> bool:
    """Validate by json.loads"""
    # pylint: disable=broad-except
    # noinspection PyBroadException
    try:
        _ = json.loads(code)
        return True
    except Exception:
        return False


def parses_as_xml(code: str) -> bool:
    """If it parses as xml, it probably is xml or someting like it"""
    if "<" not in code or ">" not in code:
        # I don't care if a text fragment is xml in some sense
        return False
    # pylint: disable=broad-except
    # noinspection PyBroadException
    try:
        _ = defusedxml.ElementTree.fromstring(code, forbid_dtd=True)
        return True
    except Exception:  # as ex:
        # print(ex)
        return False


def language_by_parsing(code: str) -> List[str]:
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
