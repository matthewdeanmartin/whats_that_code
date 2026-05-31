from whats_that_code.parsing_based import language_by_parsing, parses_as_json, parses_as_python, parses_as_xml


def test_parses_as_python_valid():
    assert parses_as_python("x = 1\nprint(x)")


def test_parses_as_python_invalid():
    assert not parses_as_python("def (((broken")


def test_parses_as_json_valid():
    assert parses_as_json('{"key": "value"}')


def test_parses_as_json_valid_array():
    assert parses_as_json("[1, 2, 3]")


def test_parses_as_json_invalid():
    assert not parses_as_json("not json at all")


def test_parses_as_xml_valid():
    assert parses_as_xml("<root><child/></root>")


def test_parses_as_xml_no_brackets():
    assert not parses_as_xml("no brackets here")


def test_parses_as_xml_invalid():
    assert not parses_as_xml("<unclosed>")


def test_parses_as_xml_rejects_html_root():
    """Valid XHTML should NOT be reported as XML."""
    xhtml = '<?xml version="1.0"?><html><head/><body><p>hi</p></body></html>'
    assert not parses_as_xml(xhtml)


def test_parses_as_xml_rejects_xhtml_namespace():
    """XHTML with explicit namespace should NOT be reported as XML."""
    xhtml = (
        '<?xml version="1.0"?>'
        '<html xmlns="http://www.w3.org/1999/xhtml">'
        "<head/><body/>"
        "</html>"
    )
    assert not parses_as_xml(xhtml)


def test_parses_as_xml_accepts_non_html_root():
    """XML with a non-html root element should still be XML."""
    assert parses_as_xml("<feed><entry/></feed>")


def test_language_by_parsing_empty():
    assert language_by_parsing("") == []
    assert language_by_parsing("   ") == []


def test_language_by_parsing_python():
    result = language_by_parsing("x = 1\nprint(x)")
    assert "python" in result


def test_language_by_parsing_json():
    result = language_by_parsing('{"a": 1}')
    assert "json" in result


def test_language_by_parsing_xml():
    result = language_by_parsing("<root/>")
    assert "xml" in result
