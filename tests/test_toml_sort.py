"""Test the toml_sort module"""

from toml_sort import sort_toml


def test_sort_toml_is_str() -> str:
    """Take a TOML string, sort it, and return the sorted string"""
    assert isinstance(sort_toml("[hello]"), str)
