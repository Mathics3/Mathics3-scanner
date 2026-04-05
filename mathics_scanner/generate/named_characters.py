#!/usr/bin/env python
# This scripts reads the data from named-characters and converts it to the
# format used by the library internally

import json
import os
import re
import sys
from pathlib import Path

import click
import yaml

# Silence warnings about JSON tables not existing
os.environ["MATHICS3_TABLE_GENERATION"] = "true"
from mathics_scanner.version import __version__  # noqa


def build_unicode_to_ascii_table(data):
    """
    Collect unicode-equivalent and wl-unicode characters
    in data, and associate them to an ascii string.
    """
    result = {}
    for key, entry in data.items():
        # First, look at the ascii entry
        ascii_equiv = entry.get("ascii", None)
        # If there is no ascii entry, try with
        # esc-alias
        if ascii_equiv is None:
            ascii_equiv = entry.get("esc-alias", None)
        # otherwise, use the NameCharacter form:
        if ascii_equiv is None:
            ascii_equiv = rf"\[{key}]"

        unicode_equivalent = entry.get("unicode-equivalent", None)
        if unicode_equivalent is not None:
            # not already an ascii character
            if unicode_equivalent != ascii_equiv and (
                len(unicode_equivalent) != 1 or ord(unicode_equivalent) > 127
            ):
                result[unicode_equivalent] = ascii_equiv
        wl_unicode = entry.get("wl-unicode", None)
        if wl_unicode is not None and wl_unicode not in result:
            # not ascii
            if wl_unicode != ascii_equiv and (
                len(wl_unicode) != 1 or ord(wl_unicode) > 127
            ):
                result[wl_unicode] = ascii_equiv

    return result


def re_from_keys(d: dict) -> str:
    """
    Takes dictionary whose keys are all strings and returns a regex that
    matches any of the keys
    """

    # The sorting is necessary to prevent the shorter keys from obscuring the
    # longer ones when pattern-matchig
    return "|".join(sorted(map(re.escape, d.keys()), key=lambda k: (-len(k), k)))


def get_plain_text(char_name: str, char_data: dict, use_unicode: bool) -> str:
    """:param char_name: named character to look up.
    :param char_data: translation dictionary.

    :returns: if use_unicode is True, then return the standard unicode equivalent
    of the name if there is one.

    Note that this may sometimes be different than the WL unicode
    value. An example of this is DifferentialD.

    If use_unicode is False, return char_name if it consists of only
    ASCII characters.

    Failing above, return \\[char_name]]
    """
    uni = char_data.get("unicode-equivalent", char_data.get("ascii"))

    if uni is not None:
        if use_unicode:
            return uni

        # If all of the characters in the unicode representation are valid
        # ASCII then return the unicode representation
        elif all(ord(c) < 127 for c in uni):
            return uni

    return f"\\[{char_name}]"


def compile_tables(data: dict) -> dict:
    """
    Compiles the general table into the tables used internally by the library.
    This facilitates fast access of this information by clients needing this
    information.
    """

    # Multiple entries in the YAML table are redundant in the following sense:
    # when a character has a plain-text equivalent but the plain-text
    # equivalent is equal to it's WL unicode representation (i.e. the
    # "wl-unicode" field is the same as the "unicode-equivalent" field) then it
    # is considered rendundant for us, since no conversion is needed.
    #
    # As an optimization, we explicit remove any redundant characters from all
    # JSON tables. This makes the tables smaller (therefore easier to load), as
    # well as the correspond regex patterns. This implies that not all
    # characters that have a unicode equivalent are included in `wl_to_ascii`
    # or `wl_to_unicode_dict`. Furthermore, this implies that not all
    # characters that have a unicode inverse are included in
    # `unicode_to_wl_dict`

    for k, v in data.items():
        if "esc-alias" in v:
            assert "wl-unicode" in v, f"esc-alias {k} needs wl-unicode"
        if v.get("is-letter-like"):
            assert "wl-unicode" in v, f"is-letter-like {k} needs wl-unicode"

    # ESC sequence aliases dictionary entry
    aliased_characters = {
        v["esc-alias"]: v.get("unicode-equivalent", v.get("wl-unicode"))
        for v in data.values()
        if "esc-alias" in v
    }

    # unicode-to-ascii
    unicode_to_ascii = build_unicode_to_ascii_table(data)

    # WL to AMS LaTeX (math mode) characters
    wl_to_amslatex = {
        v["wl-unicode"]: v.get("amslatex")
        for v in data.values()
        if "amslatex" in v and "wl-unicode" in v
    }

    # WL to LaTeX text-mode characters
    wl_to_latex = {
        v["wl-unicode"]: v.get("latex")
        for v in data.values()
        if "latex" in v and "wl-unicode" in v
    }

    # operator-to-unicode dictionary entry
    operator_to_precedence = {
        v["operator-name"]: v["precedence"]
        for v in data.values()
        if "operator-name" in v and "precedence" in v
    }

    # operator-to-unicode dictionary entry
    operator_to_unicode = {
        v["operator-name"]: v.get("unicode-equivalent", v.get("ascii"))
        for v in data.values()
        if "operator-name" in v and ("unicode-equivalent" in v or "ascii" in v)
    }

    # operator-to-ascii or character symbol name
    operator_to_ascii = {
        v["operator-name"]: v.get("ascii", rf'\[{v["operator-name"]}]')
        for k, v in data.items()
        if "operator-name" in v and ("unicode-equivalent" in v or "ascii" in v)
    }

    # Conversion from unicode or ascii to wl dictionary entry.
    # We filter the dictionary after it's first created to redundant entries
    unicode_to_wl_dict = {
        v.get("unicode-equivalent", v.get("ascii")): v.get("wl-unicode", v.get("ascii"))
        for v in data.values()
        if ("unicode-equivalent" in v or "ascii" in v) and v["has-unicode-inverse"]
    }
    unicode_to_wl_dict = {k: v for k, v in unicode_to_wl_dict.items() if k != v}
    unicode_to_wl_re = re_from_keys(unicode_to_wl_dict)

    # Unicode string containing all letterlikes values dictionary entry
    letterlikes = "".join(
        v.get("unicode-equivalent", v.get("wl-unicode"))
        for v in data.values()
        if v["is-letter-like"]
    )

    # All supported named characters dictionary entry
    named_characters = {
        k: v.get("unicode-equivalent", v.get("wl-unicode"))
        for k, v in data.items()
        if "wl-unicode" in v
    }

    # WL to AMS LaTeX (math-mode) characters
    amslatex_named_characters = {
        k: v.get("amslatex") for k, v in data.items() if "amslatex" in v
    }

    # WL to LaTeX text-mode characters
    latex_named_characters = {
        k: v.get("latex") for k, v in data.items() if "latex" in v
    }

    operator_names = sorted([k for k, v in data.items() if "operator-name" in v])

    ascii_operators = []
    ascii_operator_to_character_symbol = {}
    ascii_operator_to_symbol = {}
    ascii_operator_to_unicode = {}
    ascii_operator_to_wl_unicode = {}

    builtin_constants = {
        v["unicode-equivalent"]: k
        for k, v in data.items()
        if v.get("is-builtin-constant")
    }

    for operator_name in operator_names:
        # Operators with ASCII sequences list entry
        v = data[operator_name]
        ascii_name = v.get("ascii", None)
        if ascii_name is not None:
            ascii_operators.append(v["ascii"])
            ascii_operator_to_character_symbol[ascii_name] = rf'\[{v["operator-name"]}]'
            ascii_operator_to_symbol[ascii_name] = v["operator-name"]
            # Mathics core stores the ascii operator value, Use that to get standard unicode
            # symbol, and failing use the ASCII sequence.
            ascii_operator_to_unicode[ascii_name] = v.get(
                "unicode-equivalent", v.get("ascii")
            )
            ascii_operator_to_wl_unicode[ascii_name] = v.get(
                "wl-unicode", v.get("ascii")
            )

    # unicode-to-amslatex dictionary entry
    unicode_to_amslatex = {
        character_info["unicode-equivalent"]: character_info["amslatex"]
        for character_info in data.values()
        if character_info.get("unicode-equivalent") and character_info.get("amslatex")
    }

    # unicode-to-latex dictionary entry
    unicode_to_latex = {
        character_info["unicode-equivalent"]: character_info["latex"]
        for character_info in data.values()
        if character_info.get("unicode-equivalent") and character_info.get("latex")
    }

    # unicode-to-operator dictionary entry
    unicode_to_operator = {
        v.get("unicode-equivalent", v.get("ascii")): v["operator-name"]
        for v in data.values()
        if "operator-name" in v
    }

    # Conversion from WL to the fully qualified names dictionary entry
    wl_to_ascii_dict = {
        v["wl-unicode"]: get_plain_text(k, v, use_unicode=False)
        for k, v in data.items()
        if "wl-unicode" in v
    }
    wl_to_ascii_dict = {k: v for k, v in wl_to_ascii_dict.items() if k != v}
    wl_to_ascii_re = re_from_keys(wl_to_ascii_dict)

    # Conversion from Character Name to WL unicode
    name_to_wl_unicode = {
        name: info["wl-unicode"] for name, info in data.items() if "wl-unicode" in info
    }

    # Conversion from wl to unicode dictionary entry
    # We filter the dictionary after it's first created to redundant entries
    wl_to_unicode_dict = {
        v["wl-unicode"]: get_plain_text(k, v, use_unicode=True)
        for k, v in data.items()
        if "wl-unicode" in v
    }
    wl_to_unicode_dict = {k: v for k, v in wl_to_unicode_dict.items() if k != v}
    wl_to_unicode_re = re_from_keys(wl_to_unicode_dict)

    return {
        "aliased-characters": aliased_characters,
        "amslatex-named-characters": amslatex_named_characters,
        "ascii-operators": ascii_operators,
        "ascii-operator-to-symbol": ascii_operator_to_symbol,
        "ascii-operator-to-character-symbol": ascii_operator_to_character_symbol,
        "ascii-operator-to-unicode": ascii_operator_to_unicode,
        "ascii-operator-to-wl-unicode": ascii_operator_to_wl_unicode,
        "builtin-constants": builtin_constants,
        "latex-named-characters": latex_named_characters,
        "letterlikes": letterlikes,
        "name-to-wl-unicode": name_to_wl_unicode,
        "named-characters": named_characters,
        "operator-names": operator_names,
        "operator-to-precedence": operator_to_precedence,
        "operator-to-ascii": operator_to_ascii,
        "operator-to-unicode": operator_to_unicode,
        "unicode-to-amslatex": unicode_to_amslatex,
        "unicode-to-ascii": unicode_to_ascii,
        "unicode-to-latex": unicode_to_latex,
        "unicode-operators": unicode_to_operator,
        "unicode-to-wl-dict": unicode_to_wl_dict,
        "unicode-to-wl-re": unicode_to_wl_re,
        "wl-to-ascii-dict": wl_to_ascii_dict,
        "wl-to-ascii-re": wl_to_ascii_re,
        "wl-to-amslatex": wl_to_amslatex,
        "wl-to-latex": wl_to_latex,
        "wl-to-unicode-dict": wl_to_unicode_dict,
        "wl-to-unicode-re": wl_to_unicode_re,
    }


DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data"

ALL_FIELDS = [
    "aliased-characters",
    "amslatex-named-characters",
    "ascii-operators",
    "ascii-operator-to-character-symbol",
    "ascii-operator-to-symbol",
    "ascii-operator-to-unicode",
    "ascii-operator-to-wl-unicode",
    # "builtin-constants",  # not used yet
    "latex-named-characters",
    "letterlikes",
    "name-to-wl-unicode",
    "named-characters",
    "operator-names",
    "operator-to-amslatex",  # This is really an alias
    "operator-to-ascii",
    "operator-to-precedence",
    "operator-to-unicode",
    #   "unicode-operators",  # not used yet
    "unicode-to-amslatex",
    "unicode-to-ascii",
    "unicode-to-latex",
    "unicode-to-wl-dict",
    "unicode-to-wl-re",
    "wl-to-ascii-dict",
    "wl-to-ascii-re",
    "wl-to-amslatex",
    "wl-to-latex",
    "wl-to-unicode-dict",
    "wl-to-unicode-re",
]


@click.command()
@click.version_option(version=__version__)  # NOQA
@click.option(
    "--field",
    "-f",
    multiple=True,
    required=False,
    help="Select which fields to include in JSON.",
    show_default=True,
    type=click.Choice(ALL_FIELDS),
    default=ALL_FIELDS,
)
@click.option(
    "--output",
    "-o",
    show_default=True,
    type=click.Path(writable=True),
    default=DEFAULT_DATA_DIR / "named-characters.json",
)
@click.argument(
    "data_dir", type=click.Path(readable=True), default=DEFAULT_DATA_DIR, required=False
)
def main(field, output, data_dir):
    with (
        open(data_dir / "named-characters.yml", "r", encoding="utf8") as i,
        open(output, "w") as o,
    ):
        # Load the YAML data.
        data = yaml.load(i, Loader=yaml.FullLoader)

        # Precompile the tables.
        data = compile_tables(data)

        # Until mathics-core is synced up, operator-to-amslatex
        # is the same as unicode-to-ams-latex.
        if "operator-to-amslatex" in field:
            field = list(field)
            field.remove("operator-to-amslatex")
            field.append("unicode-to-amslatex")

        # Remove the fields that aren't wanted
        for f in set(ALL_FIELDS) - {"operator-to-amslatex"}:
            if f not in field:
                del data[f]

        # Dump the preprocessed dictionaries to disk as JSON.
        json.dump(data, o)


if __name__ == "__main__":
    main(sys.argv[1:])
