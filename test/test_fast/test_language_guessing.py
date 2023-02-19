from whats_that_code.election import guess_language_all_methods
from whats_that_code.keyword_based import guess_by_keywords
from whats_that_code.guess_by_code_and_tags import assign_extension
from whats_that_code.pygments_based import language_by_pygments
from whats_that_code.regex_based import language_by_regex_features


def test_assign_extension():
    extension, language = assign_extension("print('hello')", tags=["python", "stuff"])
    assert extension == ".py"


def test_assign_extension2():
    extension, language = assign_extension("", tags=["python", "stuff"])
    assert extension == ""


def test_assign_extension3():
    # bash is hard to guess.
    extension, language = assign_extension("pip install foo", tags=["python", "stuff"])
    assert extension == ".py"

    # extension,language= assign_extension("public static void class Foo {System.out.println('yo')}",True)
    # assert extension==".java"


def test_election_bash():
    # why did this stop working?
    assert guess_language_all_methods("sudo yum install pip", file_name="foo.sh")


def test_election():
    assert guess_language_all_methods(
        "public static void main(args[]){\n   system.out.writeln('');}"
    )


def test_election2():
    assert guess_language_all_methods("def yo():\n   print('hello')", file_name="yo.py")


# not handling file names with spaces in them?!
# def test_election3():
#     assert guess_language_all_methods(
#         "sudo yum install pip", surrounding_text="The file is named foo.py"
#     )


def test_guess_by_keywords():
    assert "python" in guess_by_keywords("def class pip")


def test_language_by_regex_features():
    assert "python" in language_by_regex_features("def foo():\n   print('yo')")


def test_language_by_pygments():
    assert language_by_pygments(
        """// Your First C++ Program

#include <iostream>

int main() {
    std::cout << "Hello World!";
    return 0;
}"""
    )
