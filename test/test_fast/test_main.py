import sys

import pytest

from whats_that_code.__main__ import main


def test_main_with_code(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["whats_that_code", "-c", "def foo(): pass"])
    result = main()
    assert result == 0


def test_main_with_file(tmp_path, monkeypatch):
    f = tmp_path / "hello.py"
    f.write_text("print('hello')\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["whats_that_code", "-f", str(f)])
    result = main()
    assert result == 0


def test_main_unknown_language(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["whats_that_code", "-c", "zzz ??? !!!"])
    result = main()
    # May or may not find a language — just shouldn't crash
    assert result in (0, 1)


def test_main_verbose(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["whats_that_code", "--verbose", "-c", "def foo(): pass"])
    result = main()
    assert result == 0


def test_main_returns_1_for_no_match(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["whats_that_code", "-c", ""])
    result = main()
    assert result == 1
    captured = capsys.readouterr()
    assert "Unknown" in captured.err


def test_main_no_args(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["whats_that_code"])
    with pytest.raises(SystemExit):
        main()
