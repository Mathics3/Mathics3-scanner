from test.helper import json_data, yaml_data

from mathics_scanner.characters import (
    replace_unicode_with_wl as unicode_to_wl,
    replace_wl_with_plain_text as wl_to_unicode,
)


def test_ascii_fields_in_json():
    """
    Check that ASCII fields in JSON tables are ASCII.
    """
    for ascii_key_dict in (
        "aliased-characters",
        "ascii-operator-to-symbol",
        "ascii-operator-to-character-symbol",
        "ascii-operator-to-unicode",
        "ascii-operator-to-wl-unicode",
        "named-characters",
        "operator-to-ascii",
        "operator-to-unicode",
    ):
        for name in json_data[ascii_key_dict]:
            assert (
                name.isascii()
            ), f"Key name of table {ascii_key_dict} should be ASCII; is: {name}"

    for ascii_list in ("ascii-operators", "operator-names"):
        for name in json_data[ascii_list]:
            assert (
                name.isascii()
            ), f"list item of table {ascii_list} should be ASCII; is: {name}"

    for ascii_value_list in (
        "ascii-operators",
        "named-characters",
    ):
        for value in json_data[ascii_value_list]:
            assert (
                value.isascii()
            ), f"Value {value} in table {ascii_value_list} should be ASCII"

    for ascii_value_list in (
        "ascii-operator-to-symbol",
        "ascii-operator-to-character-symbol",
        "builtin-constants",
        "operator-to-ascii",
        "wl-to-amslatex",
    ):
        for name, value in json_data[ascii_value_list].items():
            assert (
                value.isascii()
            ), f"Value for key {name} of table {ascii_value_list} should be ASCII; is: {value}"


def test_counts():
    letterlikes_len = len(set(json_data["letterlikes"]))
    named_characters_set = set(json_data["named-characters"].keys())
    assert letterlikes_len <= len(
        named_characters_set
    ), "Number of letter-likes should be less than the number of all named characters"

    assert set(yaml_data.keys()) >= set(
        json_data["named-characters"].keys()
    ), "There should be a named character for each WL symbol"


def test_roundtrip():
    wl_to_unicode_dict = json_data["wl-to-unicode-dict"]
    unicode_to_wl_dict = json_data["unicode-to-wl-dict"]

    for k, v in yaml_data.items():
        if v["has-unicode-inverse"]:
            assert (
                "unicode-equivalent" in v or "ascii" in v
            ), f"{k} has unicode-inverse but no unicode equivalent"
            uni = v.get("unicode-equivalent", v.get("ascii"))
            wl = v["wl-unicode"]
            assert (
                unicode_to_wl(wl_to_unicode(wl)) == wl
            ), f"key {k} unicode {uni}, {wl_to_unicode(uni)}"

            if uni != wl:
                assert (
                    uni == wl_to_unicode_dict[wl]
                ), f"key {k} unicode {uni}, {wl_to_unicode(uni)}"

                assert (
                    uni in unicode_to_wl_dict
                ), f"key {k} has a non-trivial unicode inverse but isn't included in unicode-to-wl-dict"

                assert (
                    unicode_to_wl_dict[uni] == wl
                ), f"key {k} unicode {uni}, {wl_to_unicode(uni)}"
