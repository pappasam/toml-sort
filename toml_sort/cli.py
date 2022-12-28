"""Toml Sort command line interface."""

import argparse
import sys
from argparse import ArgumentParser
from typing import Any, Dict, List, Optional, Type

import tomlkit

from .tomlsort import CommentConfiguration, TomlSort

__all__ = ["cli"]

STD_STREAM = "-"  # The standard stream
ENCODING = "UTF-8"  # Currently, we only support UTF-8


def get_version() -> str:
    """Get the program version."""
    # pylint: disable=import-outside-toplevel
    try:
        # Type checker for Python < 3.8 fails.
        # Since this ony happens here, we just ignore.
        from importlib.metadata import version  # type: ignore
    except ImportError:
        try:
            # Below ignored both because this a redefinition from above, and
            # because importlib_metadata isn't known by mypy. Ignored because
            # this is intentional.
            from importlib_metadata import version  # type: ignore
        except ImportError:
            print(
                "Error: unable to get version. "
                "If using Python < 3.8, you must install "
                "`importlib_metadata` to get the version.",
                file=sys.stderr,
            )
            sys.exit(1)
    return version("toml-sort")


def printerr(arg: str) -> None:
    """Print to stderr."""
    print(arg, file=sys.stderr)


def read_file(path: str) -> str:
    """Read contents from a file."""
    if path == STD_STREAM:
        return sys.stdin.read()
    with open(path, "r", encoding=ENCODING) as fileobj:
        return fileobj.read()


def write_file(path: str, content: str) -> None:
    """Write content to a path."""
    if path == STD_STREAM:
        print(content, end="")
        return
    with open(path, "w", encoding=ENCODING) as fileobj:
        fileobj.write(content)


def validate_and_copy(
    data: Dict[str, Any], target: Dict[str, Any], key: str, type_: Type
) -> None:
    """Validate a configuration key."""
    if key not in data:
        return
    if not isinstance(data[key], type_):
        printerr(f"Value of tool.tomlsort.{key} should be of type {type_}.")
        sys.exit(1)
    target[key] = data.pop(key)


def load_config_file() -> Dict[str, Any]:
    """Load the configuration from pyproject.toml."""
    try:
        with open("pyproject.toml", encoding="utf-8") as file:
            content = file.read()
    except OSError:
        return {}

    document = tomlkit.parse(content)
    tool_section = document.get("tool", tomlkit.document())
    toml_sort_section = tool_section.get("tomlsort", tomlkit.document())
    config = dict(toml_sort_section)

    clean_config: Dict[str, Any] = {}
    validate_and_copy(config, clean_config, "all", bool)
    validate_and_copy(config, clean_config, "in_place", bool)
    validate_and_copy(config, clean_config, "no_header", bool)
    validate_and_copy(config, clean_config, "no_footer", bool)
    validate_and_copy(config, clean_config, "no_end_of_line", bool)
    validate_and_copy(config, clean_config, "no_inline", bool)
    validate_and_copy(config, clean_config, "spaces_before_comment", int)
    validate_and_copy(config, clean_config, "check", bool)
    validate_and_copy(config, clean_config, "ignore_case", bool)

    if config:
        printerr(f"Unexpected configuration values: {config}")
        sys.exit(1)

    return clean_config


def get_parser() -> ArgumentParser:
    """Get the argument parser."""
    parser = ArgumentParser(
        prog="toml-sort",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Toml sort: a sorting utility for toml files.",
        epilog="""\
Examples:

  - **Stdin -> Stdout**: cat input.toml | toml-sort
  - **Disk -> Disk**: toml-sort -o output.toml input.toml
  - **Linting**: toml-sort --check input.toml input2.toml input3.toml
  - **Inplace Disk**: toml-sort --in-place input.toml input2.toml

Return codes:

  - 0 : success.
  - 1 : errors were found

Notes:

  - You cannot redirect from a file to itself in Bash. POSIX shells process
    redirections first, then execute commands. --in-place exists for this
    reason
""",
    )
    parser.add_argument(
        "--version",
        help="display version information and exit",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--output",
        help=f"output filepath (default: '{STD_STREAM}')",
        type=str,
    )
    parser.add_argument(
        "-a",
        "--all",
        help=(
            "sort ALL keys "
            "(default: only sort non-inline 'tables and arrays of tables')"
        ),
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--in-place",
        help="overwrite the original input file with changes",
        action="store_true",
    )
    parser.add_argument(
        "--no-header",
        help="do not keep a document's leading comments",
        action="store_true",
    )
    parser.add_argument(
        "--no-footer",
        help="do not keep a document's trailing comments",
        action="store_true",
    )
    parser.add_argument(
        "--no-end-of-line",
        help="do not keep a document's end of line comments",
        action="store_true",
    )
    parser.add_argument(
        "--no-inline",
        help="do not keep a document's inline comments",
        action="store_true",
    )
    parser.add_argument(
        "--spaces-before-comment",
        help=(
            "The number of spaces before an end of line comment. "
            "(default: 1)"
        ),
        type=int,
        choices=range(1, 5),
        default=1,
    )
    parser.add_argument(
        "--check",
        help=(
            "silently check if a file's contents would be "
            "changed by the formatter"
        ),
        action="store_true",
    )
    parser.add_argument(
        "-I",
        "--ignore-case",
        help="ignore case when sorting",
        action="store_true",
    )
    parser.add_argument(
        "filenames",
        metavar="F",
        help=(
            f"filename(s) to be processed by toml-sort (default: {STD_STREAM})"
        ),
        type=str,
        nargs="*",
    )
    parser.set_defaults(**load_config_file())
    return parser


def cli(  # pylint: disable=too-many-branches
    arguments: Optional[List[str]] = None,
) -> None:
    """Toml sort cli implementation."""
    args = get_parser().parse_args(args=arguments)  # strip command itself
    if args.version:
        print(get_version())
        sys.exit(0)

    filenames_clean = args.filenames if args.filenames else (STD_STREAM,)
    usage_errors = []

    if len(filenames_clean) > 1:
        if not (args.in_place or args.check):
            usage_errors.append(
                "'--check' or '--in-place' required if using 2+ FILENAME args"
            )
        if args.output is not None:
            usage_errors.append("'--output' not allowed with 2+ FILENAME args")
    if args.in_place and STD_STREAM in filenames_clean:
        usage_errors.append(
            f"'--in-place' not allowed with stdin FILENAME '{STD_STREAM}'"
        )
    if args.in_place and args.output is not None:
        usage_errors.append(
            "'--output' and '--in-place' cannot be used together"
        )

    if usage_errors:
        printerr("Usage error(s):")
        for errno, usage_error in enumerate(usage_errors):
            printerr(f"{errno + 1}. {usage_error}")
        sys.exit(1)

    output_clean = args.output if args.output is not None else STD_STREAM
    check_failures = []

    for filename in filenames_clean:
        original_toml = read_file(filename)
        sorted_toml = TomlSort(
            input_toml=original_toml,
            only_sort_tables=not bool(args.all),
            ignore_case=args.ignore_case,
            comment_config=CommentConfiguration(
                header=not bool(args.no_header),
                footer=not bool(args.no_footer),
                spaces_before_comment=args.spaces_before_comment,
                inline_attached=not bool(args.no_inline),
                end_of_line=not bool(args.no_end_of_line),
            ),
        ).sorted()
        if args.check:
            if original_toml != sorted_toml:
                check_failures.append(filename)
        elif args.in_place:
            write_file(filename, sorted_toml)
        elif len(filenames_clean) == 1:
            write_file(output_clean, sorted_toml)
        else:
            printerr("Uncaught error. Please submit GitHub issue:")
            printerr("<https://github.com/pappasam/toml-sort/issues>")
            sys.exit(1)

    if args.check and check_failures:
        printerr(f"{len(check_failures)} check failure(s):")
        for check_failure in check_failures:
            printerr(f"  - {check_failure}")
        sys.exit(1)
