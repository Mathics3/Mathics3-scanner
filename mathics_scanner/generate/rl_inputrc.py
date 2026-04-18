#!/usr/bin/env python3
"""
Creates GNU Readline inputrc tables for converting Wolfram Language escape
sequences to either unicode symbols or Wolfram Language fully qualified named
characters. See `Named Characters
<https://reference.wolfram.com/language/tutorial/InputAndOutputInNotebooks.html#4718>`_
for more information on character aliases.
"""
import sys

from mathics_scanner.characters import ALIASED_CHARACTERS
from mathics_scanner.characters import replace_wl_with_plain_text as r


def _escape(s: str) -> str:
    """Escapes special characters in inputrc strings"""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _format(c: str, use_unicode: bool) -> str:
    """Formats a single key-value pair"""
    key = _escape(c)
    if key == "nl":
        val = "\\n"
    else:
        val = _escape(r(ALIASED_CHARACTERS[c], use_unicode=use_unicode))

    return f'"\\e{key}\\e": "{val}"\n'


def generate_inputrc(fd=sys.stdout, use_unicode=True) -> None:
    """
    Generates inputrc files that maps Wolfram Language ESC sequence aliases to
    their corresponding plain-text representation (full Unicode or strick
    ASCII)
    """
    for alias in ALIASED_CHARACTERS:
        try:
            fd.write(_format(alias, use_unicode))
        except UnicodeEncodeError:
            sys.stderr.write("Error trying to convert alias %s; skipping\n" % alias)


def usage():
    sys.stderr.write("usage: %s {inputrc-unicode | inputrc-no-unicode}\n" % sys.argv[0])
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()

    if sys.argv[1] == "inputrc-unicode":
        default_encoding = sys.getdefaultencoding()
        if default_encoding != "utf-8":
            sys.stderr.write(
                "sys.defaultencoding() is %s so we can't generate unicode output\n"
                % (default_encoding)
            )
            sys.exit(2)
        generate_inputrc(use_unicode=True)
    elif sys.argv[1] == "inputrc-no-unicode":
        generate_inputrc(use_unicode=False)
    else:
        usage()
