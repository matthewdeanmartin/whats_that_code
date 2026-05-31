from whats_that_code.tag_based import match_tag_to_languages


def test_empty_tags():
    assert match_tag_to_languages([]) == []


def test_known_language_tag():
    result = match_tag_to_languages(["python"])
    assert "python" in result


def test_empty_string_tag():
    # Empty string tag should be skipped (covers line 15 continue branch)
    result = match_tag_to_languages([""])
    assert result == []


def test_related_tag():
    # numpy is a related tag for cython (and possibly others)
    result = match_tag_to_languages(["numpy"])
    assert len(result) > 0


def test_unknown_tag():
    result = match_tag_to_languages(["notarealthing"])
    assert result == []
