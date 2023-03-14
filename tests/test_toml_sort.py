"""Test the toml_sort module."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List

import pytest

from toml_sort import TomlSort
from toml_sort.tomlsort import (
    CommentConfiguration,
    FormattingConfiguration,
    SortConfiguration,
    SortOverrideConfiguration,
)


def test_sort_toml_is_str() -> None:
    """Take a TOML string, sort it, and return the sorted string."""
    sorted_result = TomlSort("[hello]").sorted()
    assert isinstance(sorted_result, str)


@pytest.mark.parametrize(
    "unsorted_fixture,sorted_fixture,args",
    [
        (
            "dotted-key",
            "dotted-key",
            {
                "sort_config": SortConfiguration(
                    inline_arrays=True, inline_tables=True
                ),
            },
        ),
        (
            "inline",
            "inline",
            {
                "sort_config": SortConfiguration(
                    inline_arrays=True, inline_tables=True
                ),
            },
        ),
        (
            "comment",
            "comment-comments-preserved",
            {
                "comment_config": CommentConfiguration(
                    header=False, footer=False
                )
            },
        ),
        (
            "comment",
            "comment-no-comments",
            {
                "comment_config": CommentConfiguration(
                    header=False,
                    footer=False,
                    block=False,
                    inline=False,
                )
            },
        ),
        (
            "comment",
            "comment-header-footer",
            {
                "sort_config": SortConfiguration(table_keys=False),
                "format_config": FormattingConfiguration(
                    spaces_before_inline_comment=1
                ),
            },
        ),
        (
            "from-toml-lang",
            "from-toml-lang",
            {
                "sort_config": SortConfiguration(table_keys=False),
                "format_config": FormattingConfiguration(
                    spaces_before_inline_comment=1
                ),
            },
        ),
        (
            "from-toml-lang",
            "from-toml-lang-overrides",
            {
                "sort_config": SortConfiguration(
                    inline_arrays=True, inline_tables=True
                ),
                "format_config": FormattingConfiguration(
                    spaces_before_inline_comment=1
                ),
                "sort_config_overrides": {
                    "servers.beta": SortOverrideConfiguration(
                        table_keys=False
                    ),
                    "clients.data": SortOverrideConfiguration(
                        inline_arrays=False
                    ),
                },
            },
        ),
        (
            "pyproject-weird-order",
            "pyproject-weird-order",
            {
                "sort_config": SortConfiguration(table_keys=False),
                "comment_config": CommentConfiguration(block=False),
                "format_config": FormattingConfiguration(
                    spaces_before_inline_comment=1
                ),
            },
        ),
        pytest.param(
            "weird",
            "weird",
            {
                "sort_config": SortConfiguration(table_keys=False),
                "comment_config": CommentConfiguration(
                    block=False,
                ),
                "format_config": FormattingConfiguration(
                    spaces_before_inline_comment=1
                ),
            },
            marks=[pytest.mark.xfail],
        ),
    ],
)
def test_tomlsort(
    get_fixture: Callable[[str | List[str]], Path],
    unsorted_fixture: str,
    sorted_fixture: str,
    args: Dict[str, Any],
) -> None:
    """Make sure that output of TomlSort.sorted() function matches what we
    expect."""
    path_unsorted = get_fixture(unsorted_fixture)
    path_sorted = get_fixture(["sorted", sorted_fixture])

    toml_unsorted_fixture = path_unsorted.read_text()
    toml_sorted_fixture = path_sorted.read_text()

    sort_output = TomlSort(toml_unsorted_fixture, **args).sorted()

    assert sort_output == toml_sorted_fixture
    assert TomlSort(sort_output, **args).sorted() == sort_output
