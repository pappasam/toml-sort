"""Test the CLI"""

import os

import pytest
from click.testing import CliRunner

from toml_sort.cli import cli

PATH_EXAMPLES = "tests/examples"


@pytest.mark.parametrize(
    "path_unsorted,path_sorted",
    [("from-toml-lang.toml", "defaults/from-toml-lang.toml")],
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
