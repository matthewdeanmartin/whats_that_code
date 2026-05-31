"""whats_that_code — identify source code from a string or file."""

import argparse
import logging
import sys

from whats_that_code import _version as meta
from whats_that_code.election import guess_language_all_methods

LOGGER = logging.getLogger(__name__)


def main() -> int:
    """Entry point: guess language from code string or file."""
    parser = argparse.ArgumentParser(description="Guess the programming language of a code snippet or file.")
    parser.add_argument("--version", action="version", version=f"whats_that_code {meta.__version__}")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-c", "--code", metavar="CODE", help="Source code string to identify")
    source.add_argument("-f", "--file", metavar="FILE", help="Path to source file to identify")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            code = fh.read()
        file_name = args.file
    else:
        code = args.code
        file_name = ""

    result = guess_language_all_methods(code=code, file_name=file_name)
    if result:
        print(result)
        return 0
    print("Unknown", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
