"""Test the CLI."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Callable, List, NamedTuple, Optional
from unittest import mock

import pytest

from toml_sort import cli

PATH_EXAMPLES = "tests/examples"

# NOTE: weird.toml currently exposes what I interpret to be some buggy
# functionality in AOT parsing. It seems like the latest version of tomlkit
# doesn't handle edge cases elegantly here and sometimes elements in AOT's are
# ordered randomly or sorted somewhere in tomlkit itself. I've xfail'd the test
# case for now.


class SubprocessReturn(NamedTuple):
    """Organize the return results when of running a cli subprocess."""

    stdout: str
    stderr: str
    returncode: int


def capture(
    command: List[str],
    stdin: Optional[str] = None,
) -> SubprocessReturn:
    """Capture the output of a subprocess."""
    with subprocess.Popen(
        command,
        text=True,
        encoding="UTF-8",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as proc:
        stdout, stderr = proc.communicate(input=stdin)
        return SubprocessReturn(
            stdout=stdout,
            stderr=stderr,
            returncode=proc.returncode,
        )


@pytest.mark.parametrize(
    "path_unsorted,path_sorted",
    [
        ("from-toml-lang", "sorted/from-toml-lang"),
        pytest.param("weird", "sorted/weird", marks=[pytest.mark.xfail]),
        ("pyproject-weird-order", "sorted/pyproject-weird-order"),
        ("comment", "sorted/comment-header-footer"),
        ("inline", "sorted/inline-default"),
    ],
)
def test_cli_defaults(
    get_fixture: Callable[[str | List[str]], Path],
    path_unsorted: str,
    path_sorted: str,
) -> None:
    """Test the basic cli behavior with default arguments.

    Test parameters are relative to the tests/examples directory within
    this project.
    """

    with get_fixture(path_sorted).open(encoding="UTF-8") as infile:
        expected = infile.read()
    result_filepath = capture(["toml-sort", str(get_fixture(path_unsorted))])
    assert result_filepath.returncode == 0
    assert result_filepath.stdout == expected

    with get_fixture(path_unsorted).open(encoding="UTF-8") as infile:
        original = infile.read()
    result_stdin = capture(["toml-sort"], stdin=original)
    assert result_stdin.returncode == 0
    assert result_stdin.stdout == expected


@pytest.mark.parametrize(
    "path_unsorted,path_sorted,args",
    [
        (
            "comment",
            ["sorted", "comment-no-comments"],
            ["--no-comments", "--all"],
        ),
        (
            "comment",
            ["sorted", "comment-no-comments"],
            [
                "--no-inline-comments",
                "--no-block-comments",
                "--no-header-comments",
                "--no-footer-comments",
                "--all",
            ],
        ),
        (
            "comment",
            ["sorted", "comment-comments-preserved"],
            [
                "--no-header-comments",
                "--no-footer-comments",
                "--spaces-before-inline-comment",
                "2",
                "--all",
            ],
        ),
        (
            "inline",
            ["sorted", "inline"],
            [
                "--all",
                "--spaces-before-inline-comment",
                "2",
            ],
        ),
        (
            "inline",
            ["sorted", "inline"],
            [
                "--sort-table-keys",
                "--sort-inline-array",
                "--sort-inline-table",
                "--spaces-before-inline-comment",
                "2",
            ],
        ),
        (
            "inline",
            ["sorted", "inline-no-comments-no-table-sort"],
            [
                "--no-sort-tables",
                "--sort-table-keys",
                "--sort-inline-array",
                "--sort-inline-table",
                "--no-comments",
                "--trailing-comma-inline-array",
            ],
        ),
    ],
)
def test_cli_args(
    get_fixture: Callable[[str | List[str]], Path],
    path_unsorted: str,
    path_sorted: List[str],
    args: List[str],
) -> None:
    """Test the basic cli behavior with different arguments."""

    with get_fixture(path_sorted).open(encoding="UTF-8") as infile:
        expected = infile.read()
    result_filepath = capture(
        ["toml-sort"] + args + [str(get_fixture(path_unsorted))]
    )
    assert result_filepath.returncode == 0
    assert result_filepath.stdout == expected


@pytest.mark.parametrize(
    "paths, expected_exit_code",
    (
        pytest.param(
            ["from-toml-lang.toml", "weird.toml"],
            1,
            id="multiple unsorted files failed",
        ),
        pytest.param(
            ["from-toml-lang.toml", "sorted/weird.toml"],
            1,
            id="single unsorted file failed",
        ),
        pytest.param(
            [
                "sorted/from-toml-lang.toml",
                "sorted/pyproject-weird-order.toml",
            ],
            0,
            id="none failed, no output",
        ),
    ),
)
def test_multiple_files_check(paths, expected_exit_code):
    """Unsorted files should be checked."""
    paths_unsorted = [os.path.join(PATH_EXAMPLES, path) for path in paths]
    result = capture(["toml-sort", "--check"] + paths_unsorted)
    assert result.returncode == expected_exit_code, result.stderr


def test_multiple_files_in_place(tmpdir):
    """Unsorted files should be sorted in-place."""
    paths_sorted = [
        os.path.join(PATH_EXAMPLES, "sorted/from-toml-lang.toml"),
        os.path.join(PATH_EXAMPLES, "sorted/pyproject-weird-order.toml"),
    ]

    filenames_unsorted = [
        "from-toml-lang.toml",
        "pyproject-weird-order.toml",
    ]
    temp_paths_unsorted = []
    for filename in filenames_unsorted:
        orig_path = os.path.join(PATH_EXAMPLES, filename)
        temp_path = tmpdir / filename
        shutil.copy(orig_path, temp_path)
        temp_paths_unsorted.append(str(temp_path))

    result = capture(["toml-sort", "--in-place"] + temp_paths_unsorted)
    assert result.returncode == 0, result.stderr

    for path_unsorted, path_sorted in zip(temp_paths_unsorted, paths_sorted):
        with open(path_unsorted, encoding="UTF-8") as file_unsorted:
            actual = file_unsorted.read()
        with open(path_sorted, encoding="UTF-8") as file_sorted:
            expected = file_sorted.read()
        assert actual == expected


@pytest.mark.parametrize(
    "options",
    (
        pytest.param(
            [],
            id="--check or --in-place must be specified",
        ),
        pytest.param(
            ["--check", "--output", "output.toml"],
            id="cannot specify output with --check",
        ),
        pytest.param(
            ["--in-place", "--output", "output.toml"],
            id="cannot specify output with --in-place",
        ),
    ),
)
def test_multiple_files_and_errors(options):
    """Test errors if two or more files are given."""
    paths = [
        os.path.join(PATH_EXAMPLES, "from-toml-lang.toml"),
        os.path.join(PATH_EXAMPLES, "weird.toml"),
    ]
    result = capture(["toml-sort"] + options + paths)
    assert result.returncode == 1, result.stdout


def test_load_config_file_read():
    """Test no error if pyproject.toml cannot be read."""
    with mock.patch("toml_sort.cli.open", side_effect=OSError):
        assert not cli.load_config_file()


@pytest.mark.parametrize(
    "toml,expected",
    [
        ("", {}),
        ("[tool.other]\nfoo=2", {}),
        ("[tool.tomlsort]", {}),
        ("[tool.tomlsort]\nall=true", {"all": True}),
        (
            "[tool.tomlsort]\nspaces_before_inline_comment=4",
            {"spaces_before_inline_comment": 4},
        ),
    ],
)
def test_load_config_file(toml, expected):
    """Test load_config_file."""
    open_mock = mock.mock_open(read_data=toml)
    with mock.patch("toml_sort.cli.open", open_mock):
        assert cli.load_config_file() == expected


@pytest.mark.parametrize(
    "toml", ["[tool.tomlsort]\nunknown=2", "[tool.tomlsort]\nall=42"]
)
def test_load_config_file_invalid(toml, capsys):
    """Test error if pyproject.toml is not valid."""
    open_mock = mock.mock_open(read_data=toml)
    with mock.patch("toml_sort.cli.open", open_mock):
        with pytest.raises(SystemExit):
            cli.load_config_file()
        captured = capsys.readouterr()
        assert "validation error for tool.tomlsort" in captured.err
