from whats_that_code.election import guess_language_all_methods
from whats_that_code.extension_based import guess_by_extension

SPHINX_MAKEFILE = """# Minimal makefile for Sphinx documentation
#
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

help:
\t@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

%: Makefile
\t@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
"""


def test_empty_inputs():
    assert guess_by_extension() == []


def test_known_extension_py():
    result = guess_by_extension(file_name="script.py")
    assert "python" in result


def test_known_extension_js():
    result = guess_by_extension(file_name="app.js")
    assert "javascript" in result


def test_unknown_extension():
    result = guess_by_extension(file_name="file.zzz")
    assert result == []


def test_unknown_name_with_no_extension():
    result = guess_by_extension(file_name="README")
    assert result == []


def test_known_name_with_no_extension():
    assert guess_by_extension(file_name="Makefile") == ["makefile"]


def test_text_with_dotted_extension():
    result = guess_by_extension(text="also see bar.js")
    assert "javascript" in result


def test_text_word_ending_in_dot():
    # word ending with "." should be skipped
    result = guess_by_extension(file_name="foo.py", text="trailing. dot.")
    assert isinstance(result, list)


def test_special_filenames_and_extensions():
    assert guess_by_extension(file_name=".env.example") == ["dotenv"]
    assert guess_by_extension(file_name="Dockerfile") == ["docker"]
    assert guess_by_extension(file_name="component.mdx") == ["markdown"]
    assert guess_by_extension(file_name=".dockerignore") == ["docker"]


def test_reported_filenames_override_misleading_content_guesses():
    cases = [
        (".env.example", "OPENAI_KEY=", "dotenv"),
        ("Dockerfile", "<?php", "docker"),
        ("component.mdx", "def example():\n    pass", "markdown"),
        ("component.mdx", 'example :: String\nexample = "hello"', "markdown"),
        (".dockerignore", ".section .text", "docker"),
    ]

    for file_name, code, expected in cases:
        assert guess_language_all_methods(code, file_name=file_name) == expected


def test_sphinx_makefile_is_not_misclassified_as_python():
    assert guess_language_all_methods(SPHINX_MAKEFILE, file_name="Makefile") == "makefile"
    assert guess_language_all_methods(SPHINX_MAKEFILE, file_name=r"C:\docs\Makefile") == "makefile"
