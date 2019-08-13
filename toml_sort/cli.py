"""Toml Sort CLI"""

import sys
import click

from . import TomlSort


@click.command()
@click.option(
    "-o",
    "--output",
    type=click.File("w"),
    default="-",
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
    "--no-header",
    is_flag=True,
    help="Do not keep a document's leading comments.",
)
@click.argument("filename", type=click.File("r"), default="-")
@click.version_option()
def cli(output, _all, no_header, filename) -> None:
    """Sort toml file FILENAME, saving results to a file, or stdout (default)

    FILENAME a filepath or standard input (-)

    Examples (non-exhaustive list):

        Read from stdin, write to stdout: cat input.toml | toml-sort

        Read from disk, write to disk   : toml-sort -o output.toml input.toml

        Read from disk, write to stdout : toml-sort input.toml
    """
    if filename.isatty():
        error_message_if_terminal = """
toml-sort: missing FILENAME, and no stdin
Usage: toml-sort [OPTIONS] [FILENAME]

Try `toml-sort --help` for more information
""".strip()
        click.echo(error_message_if_terminal, err=True)
        sys.exit(1)
    sorted_toml = TomlSort(
        input_toml=filename.read(),
        only_sort_tables=not bool(_all),
        no_header=bool(no_header),
    ).sorted()
    output.write(sorted_toml)
