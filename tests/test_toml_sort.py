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


def test_preserve_comment_text_formatting() -> None:
    original = "# init_command = [\n#     'python',\n# ]\n\nb=2 #  inline\n#    block\na=1\n#  footer  \n"
    formatter = FormattingConfiguration(normalize_comments=False)
    result = TomlSort(original, format_config=formatter).sorted()
    assert "#     'python'," in result
    assert "#  inline" in result
    assert "#    block" in result
    assert "#  footer  \n" in result
    assert "b = 2" in result
    assert TomlSort(result, format_config=formatter).sorted() == result
    assert "#     'python'," not in TomlSort(original).sorted()


@pytest.mark.parametrize(
    "original",
    [
        "a=1\n\n#foo  \nb=2\n",
        "a=1\n# orphan\n\n#foo\n[section]\nb=2\n",
        "a=[\n1,\n# orphan\n\n#foo\n2,\n]\n",
        "# header\n\n# orphan\n\n#foo\na=1\n",
    ],
)
def test_preserve_filtered_comment_text(original: str) -> None:
    formatter = FormattingConfiguration(normalize_comments=False)
    result = TomlSort(original, format_config=formatter).sorted()
    assert "#foo" in result
    assert "# foo" not in result
    assert "# orphan" not in result
    assert TomlSort(result, format_config=formatter).sorted() == result


def test_preserve_distinct_comment_spacing_and_toml_strings() -> None:
    original = (
        'text = """\n# literal text\n"""\n'
        'quoted = "# not a comment"\n'
        "a=1\n\n#foo\nb=2\n\n# foo\nc=3\n\n#\tfoo  \nd=4\n"
    )
    formatter = FormattingConfiguration(normalize_comments=False)
    result = TomlSort(original, format_config=formatter).sorted()
    assert "#foo\n" in result
    assert "# foo\n" in result
    assert "#\tfoo  \n" in result
    assert '"""\n# literal text\n"""' in result
    assert '"# not a comment"' in result
    assert TomlSort(result, format_config=formatter).sorted() == result


@pytest.mark.parametrize(
    "value",
    [
        '"# basic"',
        "'# literal'",
        '"""# multiline basic\n# line"""',
        "'" * 3 + "# multiline literal\n# line" + "'" * 3,
        '"""# extra closing quote""""',
        "'" * 3 + "# extra closing quotes" + "'" * 5,
        '"\\"# escaped quote"',
        '"__toml_sort_comment_0__"',
    ],
)
def test_comment_preservation_does_not_change_string_values(value: str) -> None:
    import tomlrt

    original = f"text = {value}\na=1\n\n#foo\nb=2\n"
    result = TomlSort(
        original, format_config=FormattingConfiguration(normalize_comments=False)
    ).sorted()
    assert tomlrt.loads(result).to_dict() == tomlrt.loads(original).to_dict()
    assert "#foo\n" in result


@pytest.mark.parametrize("control", ["\x00", "\x0b", "\x7f"])
def test_preserving_comments_still_rejects_invalid_toml(control: str) -> None:
    import tomlrt

    with pytest.raises(tomlrt.TOMLParseError):
        TomlSort(
            f"a=1 # invalid{control}comment\n",
            format_config=FormattingConfiguration(normalize_comments=False),
        ).sorted()


@pytest.mark.parametrize(
    "unsorted_fixture,sorted_fixture,args",
    [
        (
            "gradle-version-catalog",
            "gradle-version-catalog",
            {
                "sort_config": SortConfiguration(
                    tables=False,
                ),
            },
        ),
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
            {"comment_config": CommentConfiguration(header=False, footer=False)},
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
                    "servers.beta": SortOverrideConfiguration(table_keys=False),
                    "clients.data": SortOverrideConfiguration(inline_arrays=False),
                },
            },
        ),
        (
            "from-toml-lang",
            "from-toml-lang-first",
            {
                "sort_config": SortConfiguration(
                    inline_arrays=True,
                    inline_tables=True,
                    first=["servers", "products"],
                ),
                "format_config": FormattingConfiguration(
                    spaces_before_inline_comment=1
                ),
                "sort_config_overrides": {
                    "database": SortOverrideConfiguration(first=["ports"]),
                    "owner": SortOverrideConfiguration(first=["name", "dob"]),
                    "inline.c": SortOverrideConfiguration(first=["version"]),
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
        ),
        pytest.param(
            "single-comment",
            "../single-comment",  # Input is the same as the output
            {},
        ),
        pytest.param(
            "empty",
            "empty",
            {},
        ),
    ],
)
def test_tomlsort(
    get_fixture: Callable[[str | List[str]], Path],
    unsorted_fixture: str,
    sorted_fixture: str,
    args: Dict[str, Any],
) -> None:
    """Output of TomlSort.sorted() function matches expected."""
    path_unsorted = get_fixture(unsorted_fixture)
    path_sorted = get_fixture(["sorted", sorted_fixture])

    toml_unsorted_fixture = path_unsorted.read_text()
    toml_sorted_fixture = path_sorted.read_text()

    sort_output = TomlSort(toml_unsorted_fixture, **args).sorted()

    assert sort_output == toml_sorted_fixture
    assert TomlSort(sort_output, **args).sorted() == sort_output
