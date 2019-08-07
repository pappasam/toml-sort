"""Test the toml_sort module"""

from toml_sort import TomlSort


def test_sort_toml_is_str() -> str:
    """Take a TOML string, sort it, and return the sorted string"""
    sorted_result = TomlSort("[hello]").sorted()
    assert isinstance(sorted_result, str)
