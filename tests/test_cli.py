"""Test the CLI"""

import os
import shutil

import pytest
from click.testing import CliRunner

from toml_sort.cli import cli

PATH_EXAMPLES = "tests/examples"


@pytest.mark.parametrize(
    "path_unsorted,path_sorted",
    [
        ("from-toml-lang.toml", "defaults/from-toml-lang.toml"),
        ("weird.toml", "defaults/weird.toml"),
        ("pyproject-weird-order.toml", "defaults/pyproject-weird-order.toml"),
    ],
)
def test_cli_defaults(path_unsorted: str, path_sorted: str) -> None:
    """Test the basic cli behavior with default arguments

    Test parameters are relative to the tests/examples directory within this
    project.
    """
    path_unsorted = os.path.join(PATH_EXAMPLES, path_unsorted)
    path_sorted = os.path.join(PATH_EXAMPLES, path_sorted)
    runner = CliRunner()

    with open(path_sorted) as infile:
        expected = infile.read()
    result_filepath = runner.invoke(cli, [path_unsorted])
    assert result_filepath.exit_code == 0
    assert result_filepath.output == expected

    with open(path_unsorted) as infile:
        original = infile.read()
    result_stdin = runner.invoke(cli, input=original)
    assert result_stdin.exit_code == 0
    assert result_stdin.output == expected


@pytest.mark.parametrize(
    "paths, expected_output, expected_exit_code",
    (
        pytest.param(
            ["from-toml-lang.toml", "weird.toml"],
            [
                "File 'tests/examples/from-toml-lang.toml'"
                " would be re-formatted",
                "File 'tests/examples/weird.toml' would be re-formatted",
            ],
            1,
            id="multiple unsorted files failed",
        ),
        pytest.param(
            ["from-toml-lang.toml", "defaults/weird.toml"],
            [
                "File 'tests/examples/from-toml-lang.toml'"
                " would be re-formatted",
            ],
            1,
            id="single unsorted file failed",
        ),
        pytest.param(
            ["defaults/from-toml-lang.toml", "defaults/weird.toml"],
            [],
            0,
            id="none failed, no output",
        ),
    ),
)
def test_multiple_files_check(paths, expected_output, expected_exit_code):
    """Unsorted files should be checked."""
    paths_unsorted = [os.path.join(PATH_EXAMPLES, path) for path in paths]
    runner = CliRunner()

    result = runner.invoke(cli, ["--check"] + paths_unsorted)
    assert result.exit_code == expected_exit_code, result.output
    assert result.output.splitlines() == expected_output


def test_multiple_files_in_place(tmpdir):
    """Unsorted files should be sorted in-place."""
    paths_sorted = [
        os.path.join(PATH_EXAMPLES, "defaults/from-toml-lang.toml"),
        os.path.join(PATH_EXAMPLES, "defaults/weird.toml"),
    ]

    filenames_unsorted = [
        "from-toml-lang.toml",
        "weird.toml",
    ]
    temp_paths_unsorted = []
    for filename in filenames_unsorted:
        orig_path = os.path.join(PATH_EXAMPLES, filename)
        temp_path = tmpdir / filename
        shutil.copy(orig_path, temp_path)
        temp_paths_unsorted.append(str(temp_path))

    runner = CliRunner()

    result = runner.invoke(cli, ["--in-place"] + temp_paths_unsorted)
    assert result.exit_code == 0, result.output

    for path_unsorted, path_sorted in zip(temp_paths_unsorted, paths_sorted):
        with open(path_unsorted) as file_unsorted:
            actual = file_unsorted.read()
        with open(path_sorted) as file_sorted:
            expected = file_sorted.read()
        assert actual == expected


@pytest.mark.parametrize(
    "options, expected_output",
    (
        pytest.param(
            [],
            "--check or --in-place are required "
            "if two or more input files are given",
            id="--check or --in-place must be specified",
        ),
        pytest.param(
            ["--check", "--output", "output.toml"],
            "Cannot specify output file "
            "if two or more input files are given",
            id="cannot specify output with --check",
        ),
        pytest.param(
            ["--in-place", "--output", "output.toml"],
            "Cannot specify output file "
            "if two or more input files are given",
            id="cannot specify output with --in-place",
        ),
    ),
)
def test_multiple_files_and_errors(options, expected_output):
    """Test errors if two or more files are given."""
    paths = [
        os.path.join(PATH_EXAMPLES, "from-toml-lang.toml"),
        os.path.join(PATH_EXAMPLES, "weird.toml"),
    ]
    runner = CliRunner()

    result = runner.invoke(cli, options + paths)

    assert result.exit_code == 1, result.output
    assert expected_output in result.output.splitlines()
