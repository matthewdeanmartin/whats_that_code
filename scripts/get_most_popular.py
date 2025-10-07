"""
Top programming languages this year
"""

import requests
from bs4 import BeautifulSoup

# result =requests.get("https://pypl.github.io/PYPL.html?country=US")
#
# soup = BeautifulSoup(result.text, features="html.parser")
# table = soup.find_all("<tr>")
# print()
if __name__ == "__main__":
    ranks = """1		Python
    2		Java
    3		JavaScript
    4		C#
    5		C/C++
    6		PHP
    7		R
    8		Objective-C
    9		Swift
    10		TypeScript
    11		Matlab
    12		Kotlin
    13		Go
    14		VBA
    15		Ruby
    16		Rust
    17		Scala
    18		Visual Basic
    19		Lua
    20		Ada
    21		Dart
    22		Abap
    23		Perl
    24		Julia
    25		Groovy
    26		Cobol
    27		Haskell
    28		Delphi"""
    data = {}
    data_list = []
    for row in ranks.split("\n"):
        rank, _, language = row.split("\t")
        data[language.lower()] = rank
        data_list.append(language.lower())
    print(data)
    print(data_list)
