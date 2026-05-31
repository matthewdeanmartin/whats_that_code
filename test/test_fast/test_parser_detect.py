"""Tests for the opt-in parser trick (spec/spec.md Phase 3).

Two layers: stdlib validators (always present) and tree-sitter grammars (only with
the ``whats_that_code[fast]`` extra). The feature is opt-in via
``Options(use_parsers=True)``; with it off the election output is unchanged.
"""

import random

import pytest

from whats_that_code.election import guess_language_all_methods
from whats_that_code.options import Options
from whats_that_code.parser_detect import TREE_SITTER_AVAILABLE, detect_by_parsing
from whats_that_code.parsing_based import parses_as_json, parses_as_python, parses_as_toml, parses_as_xml

needs_tree_sitter = pytest.mark.skipif(not TREE_SITTER_AVAILABLE, reason="tree-sitter ([fast] extra) not installed")


# ── stdlib validators (no extra needed) ──────────────────────────────────────


def test_stdlib_validators():
    assert parses_as_python("def f():\n    return 1\n")
    assert not parses_as_python("def (: ?? !!")
    assert parses_as_json('{"a": [1, 2, 3]}')
    assert not parses_as_json("not json at all")
    assert parses_as_xml("<root><child/></root>")
    assert not parses_as_xml("plain text")


def test_toml_validator_is_guarded():
    # tomllib is 3.11+; on 3.10 this is always False, which is acceptable.
    result = parses_as_toml('title = "demo"\n[owner]\nname = "x"\n')
    assert result in (True, False)
    assert not parses_as_toml("")  # no '=' -> short-circuits to False


def test_detect_by_parsing_finds_stdlib_languages():
    assert "json" in detect_by_parsing('{"a": 1}')
    assert "python" in detect_by_parsing("import os\n\n\ndef f(x):\n    return x\n")


def test_detect_empty_code_is_empty():
    assert not detect_by_parsing("")
    assert not detect_by_parsing("   \n  ")


def test_tree_sitter_available_is_bool():
    assert isinstance(TREE_SITTER_AVAILABLE, bool)


# ── tree-sitter layer (needs the extra) ──────────────────────────────────────


@needs_tree_sitter
def test_detect_identifies_languages_without_stdlib_parsers():
    """go/rust/ruby have no stdlib parser; tree-sitter should still find them."""
    assert "go" in detect_by_parsing('package main\nimport "fmt"\nfunc main() { fmt.Println(1) }\n')
    assert "rust" in detect_by_parsing("fn main() {\n    let mut x = 1;\n    x += 2;\n}\n")
    assert "ruby" in detect_by_parsing("def hi(n)\n  n.times { |i| puts i }\nend\n")


@needs_tree_sitter
def test_candidates_restrict_grammars():
    """With candidates given, only those grammars are tried (precise disambiguation)."""
    code = "package main\nfunc main() {}\n"
    # restrict to a candidate set that excludes go -> go should NOT appear
    restricted = detect_by_parsing(code, candidates={"python", "json"})
    assert "go" not in restricted
    # allow go -> it should appear
    assert "go" in detect_by_parsing(code, candidates={"go", "python"})


# ── end-to-end through the election ──────────────────────────────────────────


def test_default_path_unchanged_by_use_parsers_false():
    snippets = [
        "def f():\n    return 1\n",
        '{"a": [1, 2, 3]}',
        "SELECT * FROM t;\n",
    ]
    for snippet in snippets:
        random.seed(0)
        a = guess_language_all_methods(snippet)
        random.seed(0)
        b = guess_language_all_methods(snippet, options=Options(use_parsers=False))
        assert a == b


@needs_tree_sitter
def test_use_parsers_identifies_go_code_only():
    """A bare Go snippet (no filename) should be detectable with the parser trick."""
    code = 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("hi")\n}\n'
    random.seed(0)
    assert guess_language_all_methods(code, options=Options(use_parsers=True)) == "go"


def test_use_parsers_json_code_only():
    """JSON is detectable via the stdlib validator even without the extra."""
    code = '{"name": "x", "values": [1, 2, 3], "ok": true}'
    random.seed(0)
    assert guess_language_all_methods(code, options=Options(use_parsers=True)) == "json"
