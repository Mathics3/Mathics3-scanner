#!/usr/bin/env python
# This scripts reads the data from named-characters and converts it to the
# format used by the library internally

import json
import os
import os.path as osp
import sys
from pathlib import Path

import click
import yaml

# Silence warnings about JSON tables not existing
os.environ["MATHICS3_TABLE_GENERATION"] = "true"
try:
    from mathics_scanner.version import __version__  # noqa
except ImportError:
    import ast
    from pathlib import Path

    version_file = Path(__file__).parent.parent / "version.py"
    version_content = version_file.read_text()
    version_line = [
        line for line in version_content.split("\n") if line.startswith("__version__")
    ][0]
    __version__ = ast.literal_eval(version_line.split("=")[1].strip().split("#")[0])


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

    # WL to AMS LaTeX (math mode) characters
    ascii_to_unicode = {v["ASCII"]: v["Unicode"] for v in data.values()}

    unicode_to_ascii = {v["Unicode"]: v["ASCII"] for v in data.values()}

    return {
        "ascii-to-unicode": ascii_to_unicode,
        "unicode-to-ascii": unicode_to_ascii,
    }


DEFAULT_DATA_DIR = Path(osp.normpath(osp.dirname(__file__)), "..", "data")

ALL_FIELDS = [
    "unicode-to-ascii",
    "ascii-to-unicode",
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
    default=DEFAULT_DATA_DIR / "boxing-characters.json",
)
@click.argument(
    "data_dir", type=click.Path(readable=True), default=DEFAULT_DATA_DIR, required=False
)
def main(field, output, data_dir):
    with (
        open(data_dir / "boxing-characters.yml", "r", encoding="utf8") as i,
        open(output, "w") as o,
    ):
        # Load the YAML data.
        data = yaml.load(i, Loader=yaml.FullLoader)

        # Precompile the tables.
        data = compile_tables(data)

        # Dump the preprocessed dictionaries to disk as JSON.
        json.dump(data, o)


if __name__ == "__main__":
    main(sys.argv[1:])
