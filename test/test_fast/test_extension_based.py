from whats_that_code.extension_based import guess_by_extension


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


def test_no_extension():
    result = guess_by_extension(file_name="Makefile")
    assert result == []


def test_text_with_dotted_extension():
    # file_name must have extension for text path to be reached
    result = guess_by_extension(file_name="foo.py", text="also see bar.js")
    assert isinstance(result, list)


def test_text_word_ending_in_dot():
    # word ending with "." should be skipped
    result = guess_by_extension(file_name="foo.py", text="trailing. dot.")
    assert isinstance(result, list)
