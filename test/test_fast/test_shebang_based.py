from whats_that_code.shebang_based import language_by_shebang


def test_python_shebang():
    result = language_by_shebang("#!/usr/bin/env python\nprint('hello')")
    assert "python" in result


def test_bash_shebang():
    result = language_by_shebang("#!/bin/bash\necho hello")
    assert "bash" in result


def test_no_shebang():
    result = language_by_shebang("print('hello')")
    assert result == []


def test_node_shebang():
    result = language_by_shebang("#!/usr/bin/env node\nconsole.log('hi')")
    assert "javascript" in result


def test_perl_shebang():
    result = language_by_shebang("#!/usr/bin/perl\nprint 'hi';")
    assert "perl" in result
