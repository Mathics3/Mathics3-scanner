# -*- coding: utf-8 -*-
"""
This is the tokenizer or scanner portion for the Wolfram Language.

As such, it also contains a full set of translation between Wolfram Language
named characters, their Unicode/ASCII equivalents and code-points.
"""

from mathics_scanner.characters import (
    ALIASED_CHARACTERS,
    NAMED_CHARACTERS,
    replace_box_unicode_with_ascii,
    replace_unicode_with_wl,
    replace_wl_with_plain_text,
)
from mathics_scanner.errors import (
    IncompleteSyntaxError,
    InvalidSyntaxError,
    SyntaxError,
)
from mathics_scanner.feed import (
    FileLineFeeder,
    LineFeeder,
    MultiLineFeeder,
    SingleLineFeeder,
)

# TODO: Move is_symbol_name to the characters module
# from mathics_scanner.tokeniser import Token, Tokeniser, is_symbol_name
from mathics_scanner.version import __version__

__all__ = [
    "ALIASED_CHARACTERS",
    "FileLineFeeder",
    "IncompleteSyntaxError",
    "InvalidSyntaxError",
    "LineFeeder",
    "MultiLineFeeder",
    "NAMED_CHARACTERS",
    "SingleLineFeeder",
    "SyntaxError",
    # "Token",
    # "Tokeniser",
    "__version__",
    # "is_symbol_name",
    "replace_box_unicode_with_ascii",
    "replace_unicode_with_wl",
    "replace_wl_with_plain_text",
]
