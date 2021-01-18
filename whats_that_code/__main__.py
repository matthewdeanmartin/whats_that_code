# noinspection PyPep8
"""whats_that_code/identify sourcode
Usage:
  whats_that_code <code>
  whats_that_code <file>
  so_pip (-h | --help)
  so_pip --version

Options:
  -h --help                    Show this screen.
  -v --version                 Show version.
  -c --code=<code>             Source code.
  -f --file=<file>             Path to file
  --verbose                    Show logging
  --quiet                      No informational logging

"""
import logging
import sys

import docopt

from whats_that_code import _version as meta


# Do these need to stick around?
LOGGERS = []

LOGGER = logging.getLogger(__name__)


def main() -> int:
    """Get the args object from command parameters"""
    arguments = docopt.docopt(__doc__, version=f"so_pip {meta.__version__}")
    LOGGER.debug(arguments)
    return 0


if __name__ == "__main__":
    sys.exit(main())
