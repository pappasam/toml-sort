"""Toml Sort command line interface"""

import sys

import click

from . import TomlSort

# The standard stream
_STD_STREAM = "-"


def _read_file(path: str) -> str:
    """Read contents from a file"""
    if path == _STD_STREAM:
        return sys.stdin.read()
    with open(path, "r") as fileobj:
        return fileobj.read()


def _write_file(path: str, content: str) -> None:
    """Write content to a path"""
    if path == _STD_STREAM:
        click.echo(content, nl=False)
        return
    with open(path, "w") as fileobj:
        fileobj.write(content)


# in docstring, I've placed a "\b". This causes the following lines to be
# broken as-is. See the Click documentation for more details:
# https://click.palletsprojects.com/en/7.x/documentation/#preventing-rewrapping


@click.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(file_okay=True, writable=True, allow_dash=True),
    help="The output filepath. Choose stdout with '-' (the default).",
)
@click.option(
    "-a",
    "--all",
    "_all",
    is_flag=True,
    help=(
        "Sort all keys. "
        "Default is to only sort non-inline 'tables and arrays of tables'."
    ),
)
@click.option(
    "-i",
    "--in-place",
    is_flag=True,
    help=(
        "Makes changes to the original input file. "
        "Note: you cannot redirect from a file to itself in Bash. "
        "POSIX shells process redirections first, then execute the command."
    ),
)
@click.option(
    "--no-header",
    is_flag=True,
    help="Do not keep a document's leading comments.",
)
@click.option(
    "--check",
    is_flag=True,
    help=(
        "Check if an original file is changed by the formatter. "
        "Return code 0 means it would not change. "
        "Return code 1 means it would change. "
    ),
)
@click.argument(
    "filenames",
    nargs=-1,
    type=click.Path(
        exists=True, file_okay=True, readable=True, allow_dash=True
    ),
)
@click.version_option()
def cli(output, _all, in_place, no_header, check, filenames) -> None:
    """Sort toml file FILENAME(s), writing to file(s) or stdout (default)

    FILENAME a filepath or standard input (-)

    \b
    Examples (non-exhaustive list):
      Stdin -> Stdout : cat input.toml | toml-sort
      Disk -> Disk    : toml-sort -o output.toml input.toml
      Linting         : toml-sort --check input.toml input2.toml input3.toml
      Inplace Disk    : toml-sort --in-place input.toml input2.toml
    """
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    if not filenames and sys.stdin.isatty():
        error_message_if_terminal = """
toml-sort: missing FILENAME, and no stdin
Usage: toml-sort [OPTIONS] [FILENAME]

Try `toml-sort --help` for more information
""".strip()
        click.echo(error_message_if_terminal, err=True)
        sys.exit(1)

    filenames_clean = filenames if filenames else (_STD_STREAM,)

    usage_errors = []

    if len(filenames_clean) > 1:
        if not (in_place or check):
            usage_errors.append(
                "'--check' or '--in-place' required if using 2+ FILENAME args"
            )
        if output is not None:
            usage_errors.append("'--output' not allowed with 2+ FILENAME args")
    if in_place and _STD_STREAM in filenames_clean:
        usage_errors.append("'--in-place' not allowed with stdin FILENAME '-'")
    if in_place and output is not None:
        usage_errors.append(
            "'--output' and '--in-place' cannot be used together"
        )

    if usage_errors:
        click.echo("Usage error(s):", err=True)
        for errno, usage_error in enumerate(usage_errors):
            click.echo(f"{errno + 1}. {usage_error}", err=True)
        sys.exit(1)

    output_clean = output if output is not None else _STD_STREAM
    check_failures = []

    for filename in filenames_clean:
        original_toml = _read_file(filename)
        sorted_toml = TomlSort(
            input_toml=original_toml,
            only_sort_tables=not bool(_all),
            no_header=bool(no_header),
        ).sorted()
        if check:
            if original_toml != sorted_toml:
                check_failures.append(filename)
        elif in_place:
            _write_file(filename, sorted_toml)
        elif len(filenames_clean) == 1:
            _write_file(output_clean, sorted_toml)
        else:
            click.echo("Uncaught error. Please submit GitHub issue:", err=True)
            click.echo(
                "https://github.com/pappasam/toml-sort/issues", err=True
            )
            sys.exit(1)

    if check and check_failures:
        click.echo(f"{len(check_failures)} check failure(s):", err=True)
        for check_failure in check_failures:
            click.echo(f"  - {check_failure}", err=True)
        sys.exit(1)
