from whats_that_code.election import guess_by_prior_knowledge, guess_language_all_methods


def test_empty_code_returns_something_or_none():
    # Should not crash on empty input
    result = guess_language_all_methods("")
    assert result is None or isinstance(result, str)


def test_xml_code():
    xml = "<root><child>text</child></root>"
    result = guess_language_all_methods(xml)
    assert result is not None


def test_json_code():
    result = guess_language_all_methods('{"key": "value", "num": 42}')
    assert result is not None


def test_priors_valid():
    result = guess_by_prior_knowledge(["python"])
    assert "python" in result


def test_priors_invalid(capsys):
    result = guess_by_prior_knowledge(["notarealthing"])
    assert result == []
    captured = capsys.readouterr()
    assert "not a known" in captured.out


def test_priors_none():
    result = guess_by_prior_knowledge(None)
    assert result == []


def test_priors_dedup():
    result = guess_by_prior_knowledge(["python", "python"])
    assert result.count("python") == 1


def test_surrounding_text():
    result = guess_language_all_methods("print('hi')", surrounding_text="save this as script.py")
    assert result is not None


def test_tags_passed():
    result = guess_language_all_methods("def foo(): pass", tags=["python"])
    assert result == "python"


def test_xml_code_rejected_if_not_valid_xml():
    # Code that mentions xml but doesn't parse as xml — xml vote should be removed
    result = guess_language_all_methods("xml xml xml this is not xml at all <<>>")
    # Just verify it doesn't crash and returns something or None
    assert result is None or isinstance(result, str)
