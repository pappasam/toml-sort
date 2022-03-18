"""Test the CLI."""

import os
import subprocess
from typing import List, NamedTuple, Optional

import pytest

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
        ("from-toml-lang.toml", "defaults/from-toml-lang.toml"),
        pytest.param(
            "weird.toml", "defaults/weird.toml", marks=pytest.mark.xfail
        ),
        ("pyproject-weird-order.toml", "defaults/pyproject-weird-order.toml"),
    ],
)
def test_cli_defaults(path_unsorted: str, path_sorted: str) -> None:
    """Test the basic cli behavior with default arguments.

    Test parameters are relative to the tests/examples directory within
    this project.
    """
    path_unsorted = os.path.join(PATH_EXAMPLES, path_unsorted)
    path_sorted = os.path.join(PATH_EXAMPLES, path_sorted)

    with open(path_sorted, encoding="UTF-8") as infile:
        expected = infile.read()
    result_filepath = capture(["toml-sort", path_unsorted])
    # result_filepath = invoke(args=[path_unsorted])
    print(result_filepath)
    assert result_filepath.returncode == 0
    assert result_filepath.stdout == expected

    with open(path_unsorted, encoding="UTF-8") as infile:
        original = infile.read()
    result_stdin = capture(["toml-sort"], stdin=original)
    print(result_stdin)
    assert result_stdin.returncode == 0
    assert result_stdin.stdout == expected


# @pytest.mark.parametrize(
#     "paths, expected_exit_code",
#     (
#         pytest.param(
#             ["from-toml-lang.toml", "weird.toml"],
#             1,
#             id="multiple unsorted files failed",
#         ),
#         pytest.param(
#             ["from-toml-lang.toml", "defaults/weird.toml"],
#             1,
#             id="single unsorted file failed",
#         ),
#         pytest.param(
#             [
#                 "defaults/from-toml-lang.toml",
#                 "defaults/pyproject-weird-order.toml",
#             ],
#             0,
#             id="none failed, no output",
#         ),
#     ),
# )
# def test_multiple_files_check(paths, expected_exit_code):
#     """Unsorted files should be checked."""
#     paths_unsorted = [os.path.join(PATH_EXAMPLES, path) for path in paths]
#     runner = CliRunner()

#     result = runner.invoke(cli, ["--check"] + paths_unsorted)
#     assert result.exit_code == expected_exit_code, result.output


# def test_multiple_files_in_place(tmpdir):
#     """Unsorted files should be sorted in-place."""
#     paths_sorted = [
#         os.path.join(PATH_EXAMPLES, "defaults/from-toml-lang.toml"),
#         os.path.join(PATH_EXAMPLES, "defaults/pyproject-weird-order.toml"),
#     ]

#     filenames_unsorted = [
#         "from-toml-lang.toml",
#         "pyproject-weird-order.toml",
#     ]
#     temp_paths_unsorted = []
#     for filename in filenames_unsorted:
#         orig_path = os.path.join(PATH_EXAMPLES, filename)
#         temp_path = tmpdir / filename
#         shutil.copy(orig_path, temp_path)
#         temp_paths_unsorted.append(str(temp_path))

#     runner = CliRunner()

#     result = runner.invoke(cli, ["--in-place"] + temp_paths_unsorted)
#     assert result.exit_code == 0, result.output

#     for path_unsorted, path_sorted in zip(temp_paths_unsorted, paths_sorted):
#         with open(path_unsorted, encoding="UTF-8") as file_unsorted:
#             actual = file_unsorted.read()
#         with open(path_sorted, encoding="UTF-8") as file_sorted:
#             expected = file_sorted.read()
#         assert actual == expected


# @pytest.mark.parametrize(
#     "options",
#     (
#         pytest.param(
#             [],
#             id="--check or --in-place must be specified",
#         ),
#         pytest.param(
#             ["--check", "--output", "output.toml"],
#             id="cannot specify output with --check",
#         ),
#         pytest.param(
#             ["--in-place", "--output", "output.toml"],
#             id="cannot specify output with --in-place",
#         ),
#     ),
# )
# def test_multiple_files_and_errors(options):
#     """Test errors if two or more files are given."""
#     paths = [
#         os.path.join(PATH_EXAMPLES, "from-toml-lang.toml"),
#         os.path.join(PATH_EXAMPLES, "weird.toml"),
#     ]
#     runner = CliRunner()

#     result = runner.invoke(cli, options + paths)

#     assert result.exit_code == 1, result.output
