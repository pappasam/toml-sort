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
@click.argument("filename", type=click.File("r"), default="-")
@click.version_option()
def cli(output, _all, filename) -> None:
    """Sort toml file FILENAME, saving results to a file, or stdout (default)

    FILENAME a filepath or standard input (-)

    Examples:

        Read from stdin, write to stdout:

            cat input.toml | toml-sort

        Read from file on disk, write to file on disk:

            toml-sort -o output.toml input.toml

        Read from file on disk, write to stdout

            toml-sort input.toml

        Read from stdin, write to file on disk

            cat input.toml | toml-sort -o output.toml

        Sort all keys, not just top-level / table keys

            cat input.toml | toml-sort -a
    """
    if filename.isatty():
        error_message_if_terminal = """
toml-sort: missing FILENAME, and no stdin
Usage: toml-sort [OPTIONS] [FILENAME]

Try `toml-sort --help` for more information
""".strip()
        click.echo(error_message_if_terminal, err=True)
        sys.exit(1)
    only_sort_tables = not bool(_all)
    toml_content = filename.read()
    sorted_toml = TomlSort(toml_content, only_sort_tables).sorted()
    output.write(sorted_toml)
