#!/usr/bin/env python
# This scripts reads the data from named-characters and converts it to the
# format used by the library internally

import json
import os
import os.path as osp
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Tuple

import click
import yaml

# Silence warnings about JSON tables not existing
os.environ["MATHICS3_TABLE_GENERATION"] = "true"

try:
    from mathics_scanner.version import __version__  # noqa
except ImportError:
    import ast

    version_file = Path(__file__).parent.parent / "version.py"
    version_content = version_file.read_text()
    version_line = [
        line for line in version_content.split("\n") if line.startswith("__version__")
    ][0]
    __version__ = ast.literal_eval(version_line.split("=")[1].strip().split("#")[0])

OPERATOR_FIELDS = [
    "actual-precedence",
    "Precedence",
    "WolframLanguageData",
    "WolframLanguageData-corrected",
    "FullForm",
    "arity",
    "affix",
    "associativity",
    "meaningful",
]


def compile_tables(
    operator_data: Dict[str, dict], character_data: Dict[str, dict]
) -> Dict[str, dict]:
    """
    Compiles the general table into the tables used internally by the library.
    This facilitates fast access of this information by clients needing this
    information.
    """
    operator_precedences = {}
    operator_name_to_character_name = {}

    for k, v in operator_data.items():
        operator_precedences[k] = v["precedence"]

    for character_name, character_info in character_data.items():
        if (operator_name := character_info.get("operator-name")) is not None:
            operator_name_to_character_name[operator_name] = character_name

    box_operators = {}
    flat_binary_operators: Dict[str, int] = {}
    left_binary_operators: Dict[str, int] = {}
    miscellaneous_operators: Dict[str, int] = {}
    no_meaning_infix_operators = {}
    no_meaning_postfix_operators = {}
    no_meaning_prefix_operators = {}
    nonassoc_binary_operators: Dict[str, int] = {}
    operator2string = defaultdict(list)
    operator2amslatex: Dict[str, str] = {}
    postfix_operators: Dict[str, int] = {}
    prefix_operators: Dict[str, int] = {}
    right_binary_operators: Dict[str, int] = {}
    ternary_operators: Dict[str, Tuple[int, int]] = {}

    for operator_name, operator_info in operator_data.items():
        precedence = operator_info["precedence"]

        affix = operator_info["affix"]
        arity = operator_info["arity"]
        operator_dict: Dict[str, Any] = {}

        associativity = operator_info["associativity"]
        if arity == "Ternary":
            operator_dict = ternary_operators
        elif associativity == "unknown":
            operator_dict = miscellaneous_operators
        elif affix in ("Infix", "Binary"):
            if associativity is None:
                operator_dict = flat_binary_operators
            elif associativity == "left":
                operator_dict = left_binary_operators
            elif associativity == "right":
                operator_dict = right_binary_operators
            elif associativity == "non-associative":
                operator_dict = nonassoc_binary_operators
            else:
                print(
                    f"FIXME: associativity {associativity} not handled in  {operator_name}"
                )

        elif affix == "Prefix":
            operator_dict = prefix_operators
        elif affix == "Postfix":
            operator_dict = postfix_operators

        if operator_info.get("box-operator", False):
            box_operators[operator_name] = operator_info["operator"]

        # operator_dict tables are tied into the Mathics3
        # parser. Extend this table, for example to
        # include the operator unicode, requires
        # the coordination of the parser.
        if operator_dict is not None:
            operator_dict[operator_name] = precedence

        character_info = character_data.get(operator_name)
        if character_info is None:
            if (
                character_name := operator_name_to_character_name.get(operator_name)
            ) is None:
                continue
            character_info = character_data.get(character_name)

        unicode_char = character_info.get("unicode-equivalent", "no-unicode")
        ascii_chars = character_info.get("ascii", "no-ascii")

        if unicode_char != "no-unicode":
            operator2string[operator_name].append(unicode_char)
            if character_info.get("amslatex"):
                operator2amslatex[unicode_char] = character_info["amslatex"]
        if ascii_chars != "no-ascii":
            operator2string[operator_name].append(ascii_chars)

        if operator_info.get("meaningful", True) is False and (
            character_data.get(operator_name)
        ):
            if unicode_char == "no-unicode":
                if (unicode_char := character_info.get("wl-unicode")) is None:
                    print(f"FIXME: no unicode or WMA equivalent for {operator_name}")
                continue

            affix = operator_info["affix"]
            if affix == "Infix":
                no_meaning_infix_operators[operator_name] = unicode_char, precedence
            elif affix == "Postfix":
                no_meaning_postfix_operators[operator_name] = unicode_char, precedence
            elif affix == "Prefix":
                no_meaning_prefix_operators[operator_name] = unicode_char, precedence
            else:
                print(f"FIXME: affix {affix} of {operator_name} not handled")

    return {
        "box-operators": box_operators,
        "flat-binary-operators": flat_binary_operators,
        "left-binary-operators": left_binary_operators,
        "miscellaneous-operators": miscellaneous_operators,
        "no-meaning-infix-operators": no_meaning_infix_operators,
        "no-meaning-postfix-operators": no_meaning_postfix_operators,
        "no-meaning-prefix-operators": no_meaning_prefix_operators,
        "non-associative-binary-operators": nonassoc_binary_operators,
        "operator-to-amslatex": operator2amslatex,
        "operator-to-string": operator2string,
        "operator-precedences": operator_precedences,
        "postfix-operators": postfix_operators,
        "prefix-operators": prefix_operators,
        "right-binary-operators": right_binary_operators,
        "ternary-operators": ternary_operators,
    }


DEFAULT_DATA_DIR = Path(osp.normpath(osp.dirname(__file__)), "..", "data")


@click.command()
@click.version_option(version=__version__)  # NOQA
@click.option(
    "--output",
    "-o",
    show_default=True,
    type=click.Path(writable=True),
    default=DEFAULT_DATA_DIR / "operators.json",
)
@click.argument(
    "data_dir", type=click.Path(readable=True), default=DEFAULT_DATA_DIR, required=False
)
def main(output, data_dir):
    with (
        open(data_dir / "operators.yml", "r", encoding="utf8") as operator_f,
        open(data_dir / "named-characters.yml", "r", encoding="utf8") as character_f,
        open(output, "w") as o,
    ):
        # Load the YAML data.
        operator_data = yaml.load(operator_f, Loader=yaml.FullLoader)
        character_data = yaml.load(character_f, Loader=yaml.FullLoader)

        # Precompile the tables.
        data = compile_tables(operator_data, character_data)

        # Dump the preprocessed dictionaries to disk as JSON.
        json.dump(data, o)


if __name__ == "__main__":
    main(sys.argv[1:])
