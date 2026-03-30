# -*- coding: utf-8 -*-
"""This module contains character translation tables for Wolfram's
internal representation of `named characters
<https://reference.wolfram.com/language/tutorial/InputAndOutputInNotebooks.html#4718>`_
and Unicode/ASCII.

It also contains translation tables for Mathics3 operators, and Unicode
translation tables for the syntax used in Boxing operators and Boxing
expressions.
"""

import os
import os.path as osp
import re
from typing import Dict, Final

try:
    import ujson
except ImportError:
    import json as ujson


def get_srcdir() -> str:
    """Return the OS normalized real directory path for where this
    code currently resides on disk."""
    directory_path = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(directory_path)


in_generating_tables = os.environ.get("MATHICS3_TABLE_GENERATION", False)

JSON_DATA_DIR: Final[str] = osp.join(get_srcdir(), "data")

# FIXME: We need to tolerate loading this *before* tables get generated.
# because table generation may imports via importing __version__ which
# causes variables here to be
# might not run through table generation.
#
# That is why we use "get" to set default values and use "print"
# instead of raising an error.


########################################
# Load the conversion tables from disk.

NAMED_CHARACTERS_PATH: Final[str] = osp.join(JSON_DATA_DIR, "named-characters.json")

if osp.exists(NAMED_CHARACTERS_PATH):
    with open(NAMED_CHARACTERS_PATH, "r") as f:
        NAMED_CHARACTERS_COLLECTION = ujson.load(f)
else:
    if not in_generating_tables:
        print(
            "Warning: Mathics3 named character information are missing; "
            f"expected to be in {NAMED_CHARACTERS_PATH}"
        )
        print("Please run the " "mathics_scanner/generate/named_characters.py script")
    NAMED_CHARACTERS_COLLECTION = {}

OPERATORS_TABLE_PATH = osp.join(JSON_DATA_DIR, "operators.json")

if osp.exists(OPERATORS_TABLE_PATH):
    with open(osp.join(OPERATORS_TABLE_PATH), "r", encoding="utf8") as operator_f:
        OPERATOR_DATA = ujson.load(operator_f)
else:
    if not in_generating_tables:
        print(
            "Mathics3 Operator information are missing; "
            f"expected to be in {OPERATORS_TABLE_PATH}\n"
            "Please run the mathics_scanner/generate/operators.py script"
        )
    OPERATOR_DATA = {}


BOXING_CHARACTERS_PATH: Final[str] = osp.join(JSON_DATA_DIR, "boxing-characters.json")

if osp.exists(BOXING_CHARACTERS_PATH):
    with open(BOXING_CHARACTERS_PATH, "r") as f:
        BOXING_CHARACTER_DATA = ujson.load(f)
else:
    if not in_generating_tables:
        print(
            "Mathics3 boxing character information are missing; "
            f"expected to be in {BOXING_CHARACTERS_PATH}\n"
            "Please run the mathics_scanner/generate/boxing_characters.py script"
        )
    BOXING_CHARACTER_DATA = {}


########################################
# Fill in tables from read-in JSON.

# ESC sequence aliases:
ALIASED_CHARACTERS: Final[Dict[str, str]] = NAMED_CHARACTERS_COLLECTION.get(
    "aliased-characters", {}
)

BOXING_UNICODE_TO_ASCII: Final[Dict[str, str]] = BOXING_CHARACTER_DATA.get(
    "unicode-to-ascii", {}
)
BOXING_ASCII_TO_UNICODE: Final[Dict[str, str]] = BOXING_CHARACTER_DATA.get(
    "ascii-to-unicode", {}
)

# All supported named characters:
NAMED_CHARACTERS: Final[Dict[str, str]] = NAMED_CHARACTERS_COLLECTION.get(
    "named-characters", {}
)
NAME_TO_WL_UNICODE: Final[Dict[str, str]] = NAMED_CHARACTERS_COLLECTION.get(
    "name-to-wl-unicode", {}
)

replace_to_ascii_re = re.compile(
    "|".join(
        re.escape(unicode_character)
        for unicode_character in BOXING_UNICODE_TO_ASCII.keys()
    )
)


def replace_box_unicode_with_ascii(input_string):
    return "".join(BOXING_UNICODE_TO_ASCII.get(char, char) for char in input_string)


# Character ranges of letters
LETTERS: Final[str] = (
    "a-zA-Z\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u0103\u0106\u0107\
\u010c-\u010f\u0112-\u0115\u011a-\u012d\u0131\u0141\u0142\u0147\u0148\
\u0150-\u0153\u0158-\u0161\u0164\u0165\u016e-\u0171\u017d\u017e\
\u0391-\u03a1\u03a3-\u03a9\u03b1-\u03c9\u03d1\u03d2\u03d5\u03d6\
\u03da-\u03e1\u03f0\u03f1\u03f5\u210a-\u210c\u2110-\u2113\u211b\u211c\
\u2128\u212c\u212d\u212f-\u2131\u2133-\u2138\uf6b2-\uf6b5\uf6b7\uf6b9\
\uf6ba-\uf6bc\uf6be\uf6bf\uf6c1-\uf700\uf730\uf731\uf770\uf772\uf773\
\uf776\uf779\uf77a\uf77d-\uf780\uf782-\uf78b\uf78d-\uf78f\uf790\
\uf793-\uf79a\uf79c-\uf7a2\uf7a4-\uf7bd\uf800-\uf833\ufb01\ufb02"
)

# Character ranges of letterlikes
LETTERLIKES: Final[Dict[str, str]] = NAMED_CHARACTERS_COLLECTION.get("letterlikes", {})

# Conversion from WL to the fully qualified names
_wl_to_ascii: Final[Dict[str, str]] = NAMED_CHARACTERS_COLLECTION.get(
    "wl-to-ascii-dict", {}
)
_wl_to_ascii_re: Final[re.Pattern] = re.compile(
    NAMED_CHARACTERS_COLLECTION.get("wl-to-ascii-re", "")
)

# AMS LaTeX replacements
_wl_to_amstex = NAMED_CHARACTERS_COLLECTION.get("wl-to-amslatex", {})

# Conversion from WL to Unicode
_wl_to_unicode: Final[Dict[str, str]] = NAMED_CHARACTERS_COLLECTION.get(
    "wl-to-unicode-dict", {}
)
_wl_to_unicode_re: Final[re.Pattern] = re.compile(
    NAMED_CHARACTERS_COLLECTION.get("wl-to-unicode-re", "")
)

# Conversion from Unicode to WL
_unicode_to_wl: Final[Dict[str, str]] = NAMED_CHARACTERS_COLLECTION.get(
    "unicode-to-wl-dict", {}
)
_unicode_to_wl_re: Final[re.Pattern] = re.compile(
    NAMED_CHARACTERS_COLLECTION.get("unicode-to-wl-re", "")
)


# Deprecated
def replace_wl_with_plain_text(wl_input: str, use_unicode=True) -> str:
    """
    The Wolfram Language uses specific Unicode characters to represent Wolfram
    Language named characters. This function replaces all occurrences of such
    characters with their corresponding Unicode/ASCII equivalents.

    :param wl_input: The string whose characters will be replaced.
    :param use_unicode: A flag that indicates whether to use Unicode or ASCII
                        for the conversion.

    Note that the occurrences of named characters in ``wl_input`` are expect to
    be represented by Wolfram's internal scheme. For more information on Wolfram's
    representation scheme and on our own conversion scheme, please see `Listing
    of Named Characters
    <https://reference.wolfram.com/language/guide/ListingOfNamedCharacters.html>`_
    and ``implementation.rst`` respectively.
    """
    r = _wl_to_unicode_re if use_unicode else _wl_to_ascii_re
    d = _wl_to_unicode if use_unicode else _wl_to_ascii

    # The below, when use_unicode is False, will sometimes test on "ascii" twice.
    # But this routine should be deprecated.
    return r.sub(lambda m: d.get(m.group(0), _wl_to_ascii.get(m.group(0))), wl_input)


# Deprecated
def replace_unicode_with_wl(unicode_input: str) -> str:
    """
    The Wolfram Language uses specific Unicode characters to represent Wolfram
    Language named characters. This function replaces all occurrences of the
    corresponding Unicode equivalents of such characters with the characters
    themselves.

    :param unicode_input: The string whose characters will be replaced.

    Note that the occurrences of named characters in the output of
    ``replace_unicode_with_wl`` are represented using Wolfram's internal
    scheme. For more information on Wolfram's representation scheme and on our own
    conversion scheme, please see `Listing of Named Characters
    <https://reference.wolfram.com/language/guide/ListingOfNamedCharacters.html>`_
    and ``implementation.rst`` respectively.
    """
    return _unicode_to_wl_re.sub(lambda m: _unicode_to_wl[m.group(0)], unicode_input)
