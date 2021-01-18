"""
Source:
https://github.com/TomCrypto/Codex
The MIT License (MIT)

Copyright © 2016 Thomas BENETEAU

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import re
from typing import Dict, List, Pattern


def _compiled_regex(pattern: str, dotall: bool = True) -> Pattern[str]:
    """precompile some regex"""
    flags = (re.MULTILINE | re.DOTALL) if dotall else re.MULTILINE
    return re.compile(pattern, flags)


MARKERS: Dict[str, List[Pattern[str]]] = {
    # Markers applicable to several languages
    # Code, not, say, English
    "code": [
        _compiled_regex(r"^\s{2,}\S"),  # indentation
        # TODO: need to explain what is going on here as it's not obvious
        _compiled_regex(r".{,1}\s*[=/\-\+\|<\{\}\[\](\)~`_\^#]+\s*.{,1}"),
        # generic symbol capture
        _compiled_regex(r"&&|\|\||>>|<<"),
        _compiled_regex(r"\+=|-=|/=|\*=|==|!="),
        _compiled_regex(r"__\w+"),
        _compiled_regex(r"{$"),
        _compiled_regex(r"^\s*};?"),
        _compiled_regex(r"if\s*\((.*?)\)\s*{"),
        _compiled_regex(r"for\s*\((.*?)\)\s*{"),
        _compiled_regex(r"0x\d+"),
        _compiled_regex(r"=\s*0x\d+"),
    ],
    # C preprocessor markers
    "c": [
        _compiled_regex(r'^\s*#\s*include\s+("|<)[^">]+("|>)$'),
        _compiled_regex(r"^\s*#\s*include\s+<[^\.>]+>$"),
        # <> only without .h variant for C++
        _compiled_regex(r"^\s*#\s*ifn?def\s+\w+$"),
        _compiled_regex(r"^\s*#\s*if\s+(.*?)$"),
        _compiled_regex(r"^\s*#\s*if\s+defined\((.*?)$"),
        _compiled_regex(r"^\s*#\s*define \w+(.*?)$"),
        _compiled_regex(r"^\s*#\s*endif$"),
        _compiled_regex(r"^\s*#\s*undef\s+\w+$"),
        _compiled_regex(r"^\s*#\s*else$"),
        _compiled_regex(r"^\s*#\s*pragma(.*?)$"),
        # C markers
        # TODO
        _compiled_regex(r"/\*(.*?)\*/"),
    ],
    "delphi": [
        # Delphi markers
        # TODO: Delphi preprocessor markers
        _compiled_regex(r"{\$(.*?)}$"),
        _compiled_regex(r"^unit\s+\w;$"),
        _compiled_regex(r"^interface(\s+^uses(.*?))?;$"),
        _compiled_regex(r"\w+\s*=\s*(.*?);"),
        _compiled_regex(r"^\s*\w+\s*=\s*class\(\w+\)$"),
        _compiled_regex(r"^\s*\w+\s*=\s*class\(\w+\)$(.*?)^\s*end;$"),
        _compiled_regex(
            r"\s*\w+:\s*(Integer|integer|String|string|Boolean|boolean|Byte|byte|ShortInt|shortint|Word|word|SmallInt|smallint|LongWord|longword|Cardinal|cardinal|LongInt|longint|Int64|int64|Single|single|Double|double|Currency|currency|Extended|extended|Char|char|WideChar|widechar|AnsiChar|ansichar|ShortString|shortstring|AnsiString|ansistring|WideString|widestring|T\w+)(;|\))"
        ),
        _compiled_regex(
            r"(override|virtual|Override|Virtual|Overload|overload|Cdecl|cdecl|Stdcall|stdcall);"
        ),
        _compiled_regex(r"^\s*function\s*\w+(\((.*?)\))?\s*:\s*\w+;"),
        _compiled_regex(r"^\s*procedure\s*\w+(\((.*?)\))?;"),
        _compiled_regex(r"^\s*property\s+\w+\s*:\s*\w+(.*?);"),
        _compiled_regex(r"^\s*constructor Create;"),
        _compiled_regex(r"^\s*destructor Destroy;"),
        _compiled_regex(r"^\s*var(.*?)^\s*begin"),
        _compiled_regex(r"inherited(\s+\w+(\((.*?)\))?)?;"),
        _compiled_regex(r"^\s*begin(.*?)^\s*end"),
        _compiled_regex(r"\w+\s*:=\s*(.*?);"),
        _compiled_regex(r"\s<>\s"),
        _compiled_regex(r"\(\*(.*?)\*\)"),
    ],
    "python": [
        # Python markers
        _compiled_regex(
            r"^(\s*from\s+[\.\w]+)?\s*import\s+[\*\.,\w]+(,\s*[\*\.,\w]+)*(\s+as\s+\w+)?$"
        ),
        _compiled_regex(r"^\s*def\s+\w+\((.*?):$", dotall=False),
        _compiled_regex(r"^\s*if\s(.*?):$(.*?)(^\s*else:)?$", dotall=False),
        _compiled_regex(r"^\s*if\s(.*?):$(.*?)(^\s*elif:)?$", dotall=False),
        _compiled_regex(r"^\s*try:$(.*?)^\s*except(.*?):"),
        _compiled_regex(r"True|False"),
        _compiled_regex(r"==\s*(True|False)"),
        _compiled_regex(r"is\s+(None|True|False)"),
        _compiled_regex(r"^\s*if\s+(.*?)\s+in[^:\n]+:$", dotall=False),
        _compiled_regex(r"^\s*pass$"),
        _compiled_regex(r"print\((.*?)\)$", dotall=False),
        _compiled_regex(r"^\s*for\s+\w+\s+in\s+(.*?):$"),
        _compiled_regex(r"^\s*class\s+\w+\s*(\([.\w]+\))?:$", dotall=False),
        _compiled_regex(r"^\s*@(staticmethod|classmethod|property)$"),
        _compiled_regex(r"__repr__"),
        _compiled_regex(r'"(.*?)"\s+%\s+(.*?)$', dotall=False),
        _compiled_regex(r"'(.*?)'\s+%\s+(.*?)$", dotall=False),
        _compiled_regex(r"^\s*raise\s+\w+Error(.*?)$"),
        _compiled_regex(r'"""(.*?)"""'),
        _compiled_regex(r"'''(.*?)'''"),
        _compiled_regex(r"\s*# (.*?)$"),
        _compiled_regex(r"^\s*import re$"),
        _compiled_regex(r"re\.\w+"),
        _compiled_regex(r"^\s*import time$"),
        _compiled_regex(r"time\.\w+"),
        _compiled_regex(r"^\s*import datetime$"),
        _compiled_regex(r"datetime\.\w+"),
        _compiled_regex(r"^\s*import random$"),
        _compiled_regex(r"random\.\w+"),
        _compiled_regex(r"^\s*import math$"),
        _compiled_regex(r"math\.\w+"),
        _compiled_regex(r"^\s*import os$"),
        _compiled_regex(r"os\.\w+"),
        _compiled_regex(r"^\s*import os.path$"),
        _compiled_regex(r"os\.path\.\w+"),
        _compiled_regex(r"^\s*import sys$"),
        _compiled_regex(r"sys\.\w+"),
        _compiled_regex(r"^\s*import argparse$"),
        _compiled_regex(r"argparse\.\w+"),
        _compiled_regex(r"^\s*import subprocess$"),
        _compiled_regex(r"subprocess\.\w+"),
        _compiled_regex(r'^\s*if\s+__name__\s*=\s*"__main__"\s*:$'),
        _compiled_regex(r"^\s*if\s+__name__\s*=\s*'__main__'\s*:$"),
        _compiled_regex(r"self\.\w+(\.\w+)*\((.*?)\)"),
    ],
    "haskell": [
        # Haskell markers
        _compiled_regex(r"let\s+\w+\s*="),
        _compiled_regex(r"::\s+\w+\s+->"),
        _compiled_regex(r">>="),
        _compiled_regex(r"^\s*import(\s+qualified)?\s+[\.\w]+(\s*\((.*?))?$"),
        _compiled_regex(r"^\s*module\s+[\.\w]+(.*?)where$"),
        _compiled_regex(r"^\s*{-#(.*?)#-}"),
        _compiled_regex(r"^\s*\w+\s*::(.*?)$"),
        _compiled_regex(r"->\s+\[?[\w]+\]?"),
        _compiled_regex(r"\w+\s*<-\s*\w+"),
        _compiled_regex(r"\w+\s+\$\s+\w+"),
        _compiled_regex(r"\(\w+::\w+\)"),
        _compiled_regex(r"\w+\s+::\s+\w+"),
        _compiled_regex(r"\w+'"),
        _compiled_regex(r"<\$>"),
        _compiled_regex(r"^\s*=>\s+(.*?)$"),
        _compiled_regex(r"^\s*instance[^=>]+=>(.*?)where$"),
        _compiled_regex(r"^(.*?)=\s+do$", dotall=False),
        _compiled_regex(r"\+\+"),
        _compiled_regex(r"where$"),
        _compiled_regex(r"^\s*\|\s+\w+(.*?)=(.*?)$"),
        _compiled_regex(r"-- (.*?)$"),
    ],
    "xml": [
        # XML markers
        _compiled_regex(r'<\w+\s*(\s+[:\.\-\w]+="[^"]*")*\s*>(.*?)<\s*/\w+\s*>'),
        _compiled_regex(r'<\s*/\w+\s*(\s+[:\.\-\w]+="[^"]*")*\s*>(.*?)<\s*/\w+\s*>'),
        _compiled_regex(r'<\w+\s*(\s+[:\.\-\w]+="[^"]*")*\s*/>'),
        _compiled_regex(r"<\?xml(.*?)\?>"),
        _compiled_regex(r"<!--(.*?)-->"),
    ],
    "html": [
        # HTML markers
        _compiled_regex(r"<script>(.*?)</script>"),
        _compiled_regex(r"<style>(.*?)</style>"),
        _compiled_regex(r"<link>(.*?)</link>"),
        _compiled_regex(r"<title>(.*?)</title>"),
        _compiled_regex(r"<center>(.*?)</center>"),
        _compiled_regex(r"</!DOCTYPE html(.*?)>"),
        _compiled_regex(r"<br>"),
        _compiled_regex(r"&nbsp;"),
        _compiled_regex(r'<div(\s+[:\.\-\w]+="[^"]*")*>(.*?)</div>'),
        _compiled_regex(r'<span(\s+[:\.\-\w]+="[^"]*")*>(.*?)</span>'),
        _compiled_regex(r'<p(\s+[:\.\-\w]+="[^"]*")*>(.*?)</p>'),
        _compiled_regex(r'<ul(\s+[:\.\-\w]+="[^"]*")*>(.*?)</ul>'),
        _compiled_regex(r'<ol(\s+[:\.\-\w]+="[^"]*")*>(.*?)</ol>'),
        _compiled_regex(r'<li(\s+[:\.\-\w]+="[^"]*")*>(.*?)</li>'),
        _compiled_regex(r'<pre(\s+[:\.\-\w]+="[^"]*")*>(.*?)</pre>'),
        _compiled_regex(r'<h\d(\s+[:\.\-\w]+="[^"]*")*>(.*?)</h\d>'),
        _compiled_regex(r'<table(\s+[:\.\-\w]+="[^"]*")*>(.*?)</table>'),
        _compiled_regex(r'<tr(\s+[:\.\-\w]+="[^"]*")*>(.*?)</tr>'),
        _compiled_regex(r'<td(\s+[:\.\-\w]+="[^"]*")*>(.*?)</td>'),
        _compiled_regex(r"<img(.*?)>"),
    ],
    "json": [
        # JSON markers
        _compiled_regex(r'(,|{|\[)?\s*"[^"]*"\s*:\s*\[(.*?)\]'),
        _compiled_regex(r'(,|{|\[)?\s*"[^"]*"\s*:\s*{(.*?)\}'),
        _compiled_regex(r'(,|{|\[)?\s*"[^"]*"\s*:\s*[\.\-\deE]+\s*(,|}|\])'),
        _compiled_regex(r'(,|{|\[)?\s*"[^"]*"\s*:\s*"[^"]*"\s*(,|}|\])'),
        _compiled_regex(r'(,|{|\[)?\s*"[^"]*"\s*:\s*true\s*(,|}|\])'),
        _compiled_regex(r'(,|{|\[)?\s*"[^"]*"\s*:\s*false\s*(,|}|\])'),
        _compiled_regex(r'(,|{|\[)?\s*"[^"]*"\s*:\s*null\s*(,|}|\])'),
        _compiled_regex(r"(({|\[)\s({|\[))+"),
        _compiled_regex(r"((}|\])\s(}|\]))+"),
    ],
    "javascript": [
        # Javascript markers
        _compiled_regex(r"\w+\.get(.*?);"),
        _compiled_regex(r"\w+:\s*function\s*\((.*?)},?"),
        _compiled_regex(r"this\.\w+"),
        _compiled_regex(r"var\s+\w+(\s*,\s*\w+)*\s*=(.*?);$", dotall=False),
        _compiled_regex(r"[\.\w+]+\s*===\s*[\.\w+]+"),
        _compiled_regex(r"require\s*\((.*?)\);?"),
        _compiled_regex(r"undefined"),
        _compiled_regex(r"\.length"),
        _compiled_regex(r"\$\((.*?)\);"),
    ],
    # C# markers
    "c#": [
        # TODO: these are not good
        _compiled_regex(r"^\s*#region(.*?)#endregion$"),
        _compiled_regex(r"^\s*foreach\s*\((.*?)$", dotall=False),
        _compiled_regex(r"^\s*using(.*?)$"),
        _compiled_regex(r":\s*base\([^\)]+\)$"),
        _compiled_regex(r"base\.\w+"),
        _compiled_regex(r"ref\s+\w+"),
        _compiled_regex(r"^\s*namespace\s+\w+(\.\w+)+\s*\{(.*?)\};(.*?)$"),
        _compiled_regex(r"string\.\w+"),
        _compiled_regex(r"///"),
        _compiled_regex(r"///\s*<\w+>$"),
        _compiled_regex(
            r"\[\w+(\.\w+)*\(?[^\]]*\]\s*(public|protected|private|internal|\w+(\s+\w+)*\()(.*?)"
        ),
        _compiled_regex(r"(sealed\s+)?class\s*\{(.*?)\}"),
        _compiled_regex(
            r"(sealed\s+)?class\s+\w+(\.\w+)*\s*:\s*\w+(\.\w+)*\s*\{(.*?)\}"
        ),
        _compiled_regex(r"get\s*{"),
        _compiled_regex(r"set\s*{"),
        _compiled_regex(r"private\s+get\s*{"),
        _compiled_regex(r"private\s+set\s*{"),
    ],
    # C++ markers
    "cpp": [
        _compiled_regex(r"^\s*template\s*<[^>]>$"),
        _compiled_regex(r"size_t"),
        _compiled_regex(r"\w*\s*::\s*\w+"),
        _compiled_regex(r"\w+\s*::\s*\w+\((.*?)\);"),
        _compiled_regex(r"\w+\s*::\s*\w+\([^\{]+\s*\{(.*?)\w+::\w+\("),
        _compiled_regex(r"(std::)?cout\s*<<(.*?);"),
        _compiled_regex(r"(std::)?cin\s*>>(.*?);"),
        _compiled_regex(r"std::\w+"),
        _compiled_regex(r"std::\w+\((.*?)\)"),
        _compiled_regex(r"static_assert\((.*?);"),
        _compiled_regex(r"static_cast<[^>]>"),
        _compiled_regex(r"dynamic_cast<[^>]>"),
        _compiled_regex(r"nullptr"),
        _compiled_regex(r"//(.*?)$"),
        _compiled_regex(r"switch\s*\((.*?)\);"),
        _compiled_regex(r"&\(?\w+"),
        _compiled_regex(r"\w+&"),
        _compiled_regex(r"\s[A-Z0-9_]+\((.*?);"),
        _compiled_regex(r"\)\s*=\s*0;$"),
        _compiled_regex(r"~\w+\((.*?)\}"),
        _compiled_regex(r"^\s*public:(.*?)};"),
        _compiled_regex(r"^\s*private:(.*?)};"),
        _compiled_regex(r"^\s*protected:(.*?)};"),
        _compiled_regex(r"\sm_\w+"),
        _compiled_regex(r"return\s+(.*?);$"),
        _compiled_regex(r"^\s*class\s*\w+\s*:\s*public\s+\w+\s*\{(.*?)\)"),
        _compiled_regex(r"^\s*virtual\s+[^\(]+\((.*?)\)"),
        _compiled_regex(r"^\w*struct\s*(\w+\s*)?{"),
        _compiled_regex(r"\w+->\w+"),
        _compiled_regex(r"^\s*namespace\s+\w+\s*\{(.*?)\};(.*?)$"),
        _compiled_regex(r"const\s+static|static\s+const"),
        _compiled_regex(r"typedef\s+(.*?)\s+\w+\s*;$"),
        _compiled_regex(r"(i|u)(int)?\d+(_t)?"),
        _compiled_regex(r"\*\w+->"),
        _compiled_regex(r"(const\s+)?char\s*\*"),
        _compiled_regex(r"int\s+\w+"),
        _compiled_regex(r"void\s+\w+"),
        _compiled_regex(r"auto"),
    ],
    # Lua markers
    "lua": [
        # TODO
        _compiled_regex(r"--\[\[(.*?)\]\]"),
        _compiled_regex(r"local\s+\w+\s*="),
    ],
    "php": [
        # PHP markers
        _compiled_regex(r"<\?php(.*?)\?>"),
        _compiled_regex(r"<\?php"),
        _compiled_regex(r"\$\w+"),
        _compiled_regex(r"\$\w+\s+=[^;]+;"),
        _compiled_regex(r"new\s*\\\w+"),
        _compiled_regex(r"\s+\.\s+"),
        _compiled_regex(r"this->"),
    ],
    "ruby": [
        # Ruby markers
        _compiled_regex(r"^\s*def\s*[^:]+$(.*?)end$"),
        _compiled_regex(r"@[\.:\w+]"),
        _compiled_regex(r"\s:\w+"),
        _compiled_regex(r"#\{(.*?)\}"),
        _compiled_regex(r"^\s*include\s+[\.\w+]+$"),
        _compiled_regex(r"^\s*alias\s[\.\w]+\s+[\.\w]+(.*?)$"),
        _compiled_regex(r"^\s*class\s+[\.\w+]+(\s*<\s*[\.\w]+(::[\.\w]+)*)?(.*?)$"),
        _compiled_regex(r"^\s*module\s+[\.\w+]+\s*[\.\w]+(::[\.\w]+)*(.*?)$"),
    ],
    # Java markers
    "java": [
        _compiled_regex(r"\sstatic\s+final\s"),
        _compiled_regex(r"(public|protected|private)\s+synchronized\s"),
        _compiled_regex(r"synchronized\s*\([^\{]+\{(.*?)\}"),
        _compiled_regex(r"ArrayList<[\.\w+]*>"),
        _compiled_regex(r"HashMap<[\.\w+]*>"),
        _compiled_regex(r"HashSet<[\.\w+]*>"),
        _compiled_regex(r"System(\.\w+)+"),
        _compiled_regex(r"new\s+\w+(.*?);"),
        _compiled_regex(r"try\s*\{(.*?)catch[^\{]+\{"),
        _compiled_regex(r"[Ll]ogg(ing|er)"),
        _compiled_regex(r"^\s*package\s+\w+(\.\w+)*;$"),
        _compiled_regex(r"^\s*import\s+\w+(\.\w+)*;$"),
        _compiled_regex(r"(public|private|protected)\s+[^\{]*\{(.*?)\}$"),
        _compiled_regex(r"@Override"),
        _compiled_regex(r"throw new \w+\((.*?)\);\s*$"),
    ],
    # TeX markers
    "tex": [
        _compiled_regex(r"\\begin\{[^\}]+\}(.*?)\\end\{[^\}]+\}"),
        _compiled_regex(r"\\begin\{[^\}]+\}(.*?)*$", dotall=False),
        _compiled_regex(r"\\end\{[^\}]+\}(.*?)*$", dotall=False),
        _compiled_regex(r"\\\w+\s"),
        _compiled_regex(r"\\\w+({|\[)"),
        _compiled_regex(r"\\usepackage(\[[^\]]*\])?\{(.*?)\}"),
        _compiled_regex(r"^\s*%.{15,}$", dotall=False),
    ],
    # Make markers
    # MDM: trying to find out why make gets over reported.
    # MDM: trying to find out why make gets over reported.
    "make": [
        # _compiled_regex(r"^\s*[^=\n]+\s*=\s*(.*?)$"),
        # _compiled_regex(r"^\s*[^=\n]+\s*:=\s*(.*?)$"),
        # _compiled_regex(r"^\s*[^=\n]+\s*\+=\s*(.*?)$"),
        # _compiled_regex(r"^\s*[^=\n]+\s*\?=\s*(.*?)$"),
        # _compiled_regex(r"\$@|\$\*|\$^|\$<"),
        # _compiled_regex(r"\$\((.*?)\)", dotall=False),
        # _compiled_regex(r"\w+\.\w{1,3}"),
        # _compiled_regex(r"^\s*ifeq[^\n]+(.*?)^\s*endif"),
        # _compiled_regex(r"^\s*ifneq[^\n]+(.*?)^\s*endif"),
        # _compiled_regex(r"\w*%\w*"),
        # _compiled_regex(r"-[^\W\d]+"),
        _compiled_regex(r"PHONY\s*\+=(.*?)$"),
        _compiled_regex(r"\.PHONY:(.*?)$"),
    ],
}
