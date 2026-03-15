# -*- coding: utf-8 -*-
"""
Tests translation from strings to sequences of tokens.
"""

import random
import sys
from typing import List

import pytest

from mathics_scanner.errors import (
    EscapeSyntaxError,
    IncompleteSyntaxError,
    InvalidSyntaxError,
    SyntaxError,
)
from mathics_scanner.feed import MultiLineFeeder, SingleLineFeeder
from mathics_scanner.location import ContainerKind
from mathics_scanner.tokeniser import Token, Tokeniser, is_symbol_name


def check_number(source_code: str):
    token = single_token(source_code)
    assert token, Token("Number", source_code, 0)


def check_symbol(source_code: str):
    token = single_token(source_code)
    assert token, Token("Symbol", source_code, 0)


def escape_syntax_error(error_message: str):
    with pytest.raises(EscapeSyntaxError):
        tokens(error_message)


def incomplete_error(error_message: str):
    with pytest.raises(IncompleteSyntaxError):
        tokens(error_message)


def invalid_error(error_message: str):
    with pytest.raises(InvalidSyntaxError):
        tokens(error_message)


def multiline_tokens(tokenizer) -> List[Token]:
    tokens = []
    while True:
        token = tokenizer.next()
        if token.tag == "END":
            break
        else:
            tokens.append(token)
    return tokens


def scanner_error(error_message):
    with pytest.raises(SyntaxError):
        tokens(error_message)


def single_token(source_code) -> Token:
    toks = tokens(source_code)
    assert len(toks) == 1
    token = toks[0]
    return token


def tags(source_code):
    return [token.tag for token in tokens(source_code)]


def tokens(source_code) -> List[Token]:
    tokeniser = Tokeniser(
        SingleLineFeeder(source_code, "<tokens>", ContainerKind.STRING)
    )
    tokens = []
    while True:
        token = tokeniser.next()
        if token.tag == "END":
            break
        else:
            tokens.append(token)
    return tokens


def test_accuracy():
    scanner_error("1.5``")
    check_number("1.0``20")
    check_number("1.0``0")
    check_number("1.4``-20")


def test_apply():
    assert tokens("f // x") == [
        Token("Symbol", "f", 0),
        Token("Postfix", "//", 2),
        Token("Symbol", "x", 5),
    ]
    assert tokens("f @ x") == [
        Token("Symbol", "f", 0),
        Token("Prefix", "@", 2),
        Token("Symbol", "x", 4),
    ]
    assert tokens("f ~ x") == [
        Token("Symbol", "f", 0),
        Token("Infix", "~", 2),
        Token("Symbol", "x", 4),
    ]


def test_association():
    assert tokens("<|x -> m|>") == [
        Token("LessBar", "<|", 0),
        Token("Symbol", "x", 2),
        Token("Rule", "->", 4),
        Token("Symbol", "m", 7),
        Token("BarGreater", "|>", 8),
    ]


def test_backslash_named_character():
    r"""Tests \[Backslash] named character"""
    assert tokens(r"\[Backslash]") == [Token("Backslash", "\u2216", 0)]
    incomplete_error("\\")


def test_boxes():
    assert tokens("\\(1\\)") == [
        Token("LeftRowBox", "\\(", 0),
        Token("Number", "1", 2),
        Token("RightRowBox", "\\)", 3),
    ]
    assert tokens("\\(\\*RowBox[a]\\)") == [
        Token("LeftRowBox", "\\(", 0),
        Token("BoxInputEscape", "\\*", 2),
        Token("Symbol", "RowBox", 4),
        Token("RawLeftBracket", "[", 10),
        Token("Symbol", "a", 11),
        Token("RawRightBracket", "]", 12),
        Token("RightRowBox", "\\)", 13),
    ]


def test_comments():
    assert tokens("(**)") == [], "empty comment"
    assert tokens("(**)1") == [
        Token("Number", "1", 4)
    ], "empty comment with trailing text"
    assert tokens("1(*2*)") == [
        Token("Number", "1", 0)
    ], "empty comment with leading text"
    assert tokens("1 (*2*)") == [
        Token("Number", "1", 0)
    ], "empty comment with leading text and space"
    assert tokens("(* A (* nested comment *) *)") == [], "A nested comment"
    assert tokens(r"(* A \[theta] *)") == [], "Comment with valid escape sequence"
    assert tokens(r"(* A \[unknown] *)") == [], "Comment with invalid escape sequence"


def test_function():
    assert tokens("x&") == [Token("Symbol", "x", 0), Token("Function", "&", 1)]
    assert tokens("x\uf4a1") == [
        Token("Symbol", "x", 0),
        Token("Function", "\uf4a1", 1),
    ]


def test_information():
    assert tokens("??Sin") == [
        Token("QuestionQuestion", "??", 0),
        Token("NamePattern", "Sin", 2),
    ]

    assert tokens("? ?Sin") == [
        Token("PatternTest", "?", 0),
        Token("PatternTest", "?", 2),
        Token("Symbol", "Sin", 3),
    ]


def test_int_repeated():
    assert tokens("1..") == [Token("Number", "1", 0), Token("Repeated", "..", 1)]
    assert tokens("1. .") == [Token("Number", "1.", 0), Token("Dot", ".", 3)]


def test_integeral():
    assert tokens("\u222b x \uf74c y") == [
        Token("Integral", "\u222b", 0),
        Token("Symbol", "x", 2),
        Token("DifferentialD", "\uf74c", 4),
        Token("Symbol", "y", 6),
    ]


def test_is_symbol():
    assert is_symbol_name("Derivative")
    assert not is_symbol_name("98")  # symbols can't start with numbers


def test_multiline_backslash():
    source_code = "a = \\\n5"
    tokenizer = Tokeniser(
        MultiLineFeeder(source_code, "<mltokens>", ContainerKind.STRING)
    )

    assert multiline_tokens(tokenizer) == [
        Token("Symbol", "a", 0),
        Token("Set", "=", 2),
    ]
    tokenizer.source_text = tokenizer.feeder.feed()
    tokenizer.pos = 0
    assert multiline_tokens(tokenizer) == [
        Token("Number", "5", 0),
    ]
    assert tokenizer.feeder.empty(), "Feeder should note two two lines have been read"


def test_number():
    assert tags("1.5") == ["Number"]
    assert tags("1.5*^10") == ["Number"]
    check_number("0")


def test_number_base():
    check_number("8^^23")
    check_number("10*^3")
    check_number("10*^-3")
    check_number("8^^23*^2")


def test_number_big():
    for _ in range(10):
        check_number(str(random.randint(0, sys.maxsize)))
        check_number(str(random.randint(sys.maxsize, sys.maxsize * sys.maxsize)))


def test_number_real():
    check_number("1.5")
    check_number("1.5`")
    check_number("0.0")


def test_pre():
    assert tokens("++x++") == [
        Token("Increment", "++", 0),
        Token("Symbol", "x", 2),
        Token("Increment", "++", 3),
    ]


def test_precision():
    check_number("1.5`-5")
    check_number("1.5`0")
    check_number("1.5`10")


# String tests (with many more than those
# below are now in test_string_token.py
#
# def test_string():
#     check_string(r'"abc"')
#     incomplete_error(r'"abc')
#     check_string(r'"abc(*def*)"')
#     check_string(r'"a\"b\\c"')
#     incomplete_error(r'"\"')


def test_set():
    assert tokens("x = y") == [
        Token("Symbol", "x", 0),
        Token("Set", "=", 2),
        Token("Symbol", "y", 4),
    ]
    assert tokens("x /: y = z") == [
        Token("Symbol", "x", 0),
        Token("TagSet", "/:", 2),
        Token("Symbol", "y", 5),
        Token("Set", "=", 7),
        Token("Symbol", "z", 9),
    ]


def test_symbol():
    check_symbol("xX")
    check_symbol("context`name")
    check_symbol("`name")
    check_symbol("`context`name")


def test_unset():
    assert tokens("=.") == [Token("Unset", "=.", 0)]

    assert tokens("= .") == [Token("Unset", "= .", 0)]
    assert tokens("=.5") == [Token("Set", "=", 0), Token("Number", ".5", 1)]
    assert tokens("= ..") == [Token("Set", "=", 0), Token("Repeated", "..", 2)]
