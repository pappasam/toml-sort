"""Toml Sort CLI"""

import click

from . import TomlSort


def get_help() -> str:
    """Get the help string for the current click context"""
    ctx = click.get_current_context()
    help_message = ctx.get_help()
    ctx.exit()
    return help_message


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
        click.echo(get_help())
        return
    only_sort_tables = not bool(_all)
    toml_content = filename.read()
    sorted_toml = TomlSort(toml_content, only_sort_tables).sorted()
    output.write(sorted_toml)
