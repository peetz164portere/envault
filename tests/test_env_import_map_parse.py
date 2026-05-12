"""Extra edge-case tests for parse_map_string."""

import pytest
from envault.env_import_map import parse_map_string, ImportMapError


def test_parse_map_string_strips_whitespace():
    result = parse_map_string("  OLD  =  NEW  ")
    assert result == {"OLD": "NEW"}


def test_parse_map_string_multiple_equals_uses_first_split():
    # OLD=NEW=EXTRA should map OLD -> NEW=EXTRA (split on first '=')
    result = parse_map_string("OLD=NEW=EXTRA")
    assert result == {"OLD": "NEW=EXTRA"}


def test_parse_map_string_ignores_empty_segments():
    result = parse_map_string("A=B,,C=D,")
    assert result == {"A": "B", "C": "D"}


def test_parse_map_string_duplicate_old_key_last_wins():
    # Last definition of the same old key wins (dict behaviour)
    result = parse_map_string("A=B,A=C")
    assert result["A"] == "C"


def test_parse_map_string_empty_new_key_raises():
    with pytest.raises(ImportMapError, match="Empty key"):
        parse_map_string("OLD=")


def test_parse_map_string_only_commas_raises():
    with pytest.raises(ImportMapError, match="No valid mappings"):
        parse_map_string(",,,,")
