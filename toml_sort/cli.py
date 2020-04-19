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
    default=_STD_STREAM,
    show_default=True,
    help="The output filepath. Choose stdout with '-'.",
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
    """Sort toml file FILENAME, saving results to a file, or stdout (default)

    FILENAME a filepath or standard input (-)

    \b
    Examples (non-exhaustive list):
        Stdin -> Stdout : cat input.toml | toml-sort
        Disk -> Disk    : toml-sort -o output.toml input.toml
        Linting         : toml-sort --check input.toml
        Inplace Disk    : toml-sort --in-place input.toml
    """
    if not filenames:
        filenames = (_STD_STREAM,)

    if len(filenames) > 1:
        if not (in_place or check):
            click.echo(
                "--check or --in-place are required "
                "if two or more input files are given",
                err=True,
            )
            sys.exit(1)
        elif output != _STD_STREAM:
            click.echo(
                "Cannot specify output file "
                "if two or more input files are given",
                err=True,
            )
            sys.exit(1)
    elif _STD_STREAM in filenames and sys.stdin.isatty():
        error_message_if_terminal = """
toml-sort: missing FILENAME, and no stdin
Usage: toml-sort [OPTIONS] [FILENAME]

Try `toml-sort --help` for more information
""".strip()
        click.echo(error_message_if_terminal, err=True)
        sys.exit(1)
    elif in_place and _STD_STREAM in filenames:
        click.echo("Cannot format stdin in-place", err=True)
        sys.exit(1)
    elif in_place and output != _STD_STREAM:
        click.echo("Cannot specify output file with in-place", err=True)
        sys.exit(1)

    check_failed = False

    for filename in filenames:
        original_toml = _read_file(filename)
        sorted_toml = TomlSort(
            input_toml=original_toml,
            only_sort_tables=not bool(_all),
            no_header=bool(no_header),
        ).sorted()
        if check and original_toml != sorted_toml:
            click.echo(f"File '{filename}' would be re-formatted", err=True)
            check_failed = True
            continue
        if in_place:
            _write_file(filename, sorted_toml)
            continue
        if len(filenames) == 1:
            _write_file(output, sorted_toml)

    if check and check_failed:
        sys.exit(1)
