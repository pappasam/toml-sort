"""Utility functions and classes to sort toml text."""

from __future__ import annotations

import fnmatch
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

import tomlrt

__all__ = ["TomlSort"]

TomlContainer = tomlrt.Document | tomlrt.Table
TomlPath = tuple[str, ...]


def _drop_orphans(block: tuple[str | None, ...]) -> tuple[str | None, ...]:
    """Trim a leading block to its trailing attached comment run."""
    if all(comment is None for comment in block):
        return block
    index = len(block)
    while index > 0 and block[index - 1] is not None:
        index -= 1
    return block[index:]


@dataclass
class CommentConfiguration:
    """Configures how TomlSort handles comments."""

    header: bool = True
    footer: bool = True
    inline: bool = True
    block: bool = True


@dataclass
class SortConfiguration:
    """Configures how TomlSort sorts the input toml."""

    tables: bool = True
    table_keys: bool = True
    inline_tables: bool = False
    inline_arrays: bool = False
    ignore_case: bool = False
    first: List[str] = field(default_factory=list)


@dataclass
class FormattingConfiguration:
    """Configures how TomlSort formats its output."""

    spaces_before_inline_comment: int = 2
    spaces_indent_inline_array: int = 2
    trailing_comma_inline_array: bool = False


@dataclass
class SortOverrideConfiguration:
    """Configures overrides to sort configuration for a particular key."""

    table_keys: Optional[bool] = None
    inline_tables: Optional[bool] = None
    inline_arrays: Optional[bool] = None
    first: List[str] = field(default_factory=list)


class TomlSort:
    """API to manage sorting toml files."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        input_toml: str,
        comment_config: Optional[CommentConfiguration] = None,
        sort_config: Optional[SortConfiguration] = None,
        format_config: Optional[FormattingConfiguration] = None,
        sort_config_overrides: Optional[Dict[str, SortOverrideConfiguration]] = None,
    ) -> None:
        """Initializer."""
        self.input_toml = input_toml

        if comment_config is None:
            comment_config = CommentConfiguration()
        self.comment_config = comment_config

        if sort_config is None:
            sort_config = SortConfiguration()
        self._sort_config = sort_config

        if format_config is None:
            format_config = FormattingConfiguration()
        self.format_config = format_config

        if sort_config_overrides is None:
            sort_config_overrides = {}
        self.sort_config_overrides = sort_config_overrides

    def _find_config_override(
        self, path: TomlPath
    ) -> Optional[SortOverrideConfiguration]:
        """Return SortOverrideConfiguration for a particular path.

        If none exists returns None.

        Override matches are evaluated as glob patterns by the python
        fnmatch function. If there are multiple matches, return the
        exact match first otherwise return the first match.
        """
        if not path:
            return None

        path_string = ".".join(path)
        if path_string in self.sort_config_overrides:
            return self.sort_config_overrides.get(path_string)

        matches = [
            config
            for pattern, config in self.sort_config_overrides.items()
            if fnmatch.fnmatch(path_string, pattern)
        ]

        if len(matches) > 0:
            return matches[0]

        return None

    def sort_config(self, path: TomlPath = ()) -> SortConfiguration:
        """Returns the SortConfiguration to use for a particular path.

        This merges the global SortConfiguration with any matching
        SortOverrideConfiguration to give the full SortConfiguration
        that applies to this path.
        """
        override = self._find_config_override(path)
        if override is None:
            return self._sort_config

        main_config = asdict(self._sort_config)
        override_config = asdict(override)
        merged_config = {}

        for key, value in main_config.items():
            if key in override_config and override_config[key] is not None:
                merged_config[key] = override_config[key]
            else:
                merged_config[key] = value

        return SortConfiguration(**merged_config)

    def _normalized(self, value: str) -> str:
        """Normalize a value for case-sensitive or insensitive sorting."""
        return value.lower() if self._sort_config.ignore_case else value

    def _key_order(self, name: str, config: SortConfiguration) -> tuple[int, str]:
        """Build a sort key honoring `first`."""
        try:
            return (config.first.index(name), "")
        except ValueError:
            return (len(config.first), self._normalized(name))

    def _sort_container(self, container: TomlContainer, path: TomlPath) -> None:
        """Recursively sort a document, section, or inline table."""
        for key, value in container.items():
            self._sort_value(value, path + (key,))

        config = self.sort_config(path)
        if isinstance(container, tomlrt.Table) and container.is_inline:
            if config.inline_tables:
                container.sort(key=lambda name: self._key_order(name, config))
            return

        def sort_key(name: str) -> tuple[int, str]:
            enabled = config.tables if container.has_header(name) else config.table_keys
            return self._key_order(name, config) if enabled else (0, "")

        container.sort(key=sort_key)

    def _sort_array(self, array: tomlrt.Array, path: TomlPath) -> None:
        """Recursively sort an inline array."""
        for value in array:
            self._sort_value(value, path)
        if self.sort_config(path).inline_arrays:
            array.sort(key=self._array_sort_value)

    def _sort_aot(self, aot: tomlrt.AoT, path: TomlPath) -> None:
        """Recursively sort the tables in an array of tables."""
        for table in aot:
            self._sort_container(table, path)

    def _array_sort_value(self, value: Any) -> str:
        """Return a string representation for array sorting."""
        return self._normalized(str(value))

    def _sort_value(self, value: Any, path: TomlPath) -> None:
        """Recursively sort a TOML value."""
        if isinstance(value, tomlrt.Array):
            self._sort_array(value, path)
        elif isinstance(value, tomlrt.AoT):
            self._sort_aot(value, path)
        elif isinstance(value, tomlrt.Table):
            self._sort_container(value, path)

    def _filter_container_comments(self, container: TomlContainer) -> None:
        """Remove disabled comments recursively using public comment views."""
        if not self.comment_config.inline:
            container.comments.clear()
            if (
                isinstance(container, tomlrt.Table)
                and not container.is_inline
                and container.header_comment
            ):
                container.header_comment = None

        if self.comment_config.block:
            for key in list(container.leading_block):
                block = container.leading_block[key]
                attached = _drop_orphans(block)
                if attached != block:
                    container.leading_block[key] = attached
        else:
            container.leading_block.clear()

        if isinstance(container, tomlrt.Table) and not container.is_inline:
            if self.comment_config.block:
                header_block = container.header_leading_block
                attached = _drop_orphans(header_block)
                if attached != header_block:
                    container.header_leading_block = attached
            elif container.header_leading_block:
                container.header_leading_block = ()

        for value in container.values():
            self._filter_value_comments(value)

    def _filter_array_comments(self, array: tomlrt.Array) -> None:
        """Remove disabled inline-array comments recursively."""
        if not self.comment_config.inline:
            array.comments.clear()
        if self.comment_config.block:
            for index in list(array.leading_block):
                block = array.leading_block[index]
                attached = _drop_orphans(block)
                if attached != block:
                    array.leading_block[index] = attached
        else:
            array.leading_block.clear()
        for value in array:
            self._filter_value_comments(value)

    def _filter_aot_comments(self, aot: tomlrt.AoT) -> None:
        """Remove disabled comments from an array of tables."""
        for table in aot:
            self._filter_container_comments(table)

    def _filter_value_comments(self, value: Any) -> None:
        """Remove disabled comments from a TOML value."""
        if isinstance(value, tomlrt.Array):
            self._filter_array_comments(value)
        elif isinstance(value, tomlrt.AoT):
            self._filter_aot_comments(value)
        elif isinstance(value, tomlrt.Table):
            self._filter_container_comments(value)

    def sorted(self) -> str:
        """Sort a TOML string."""
        document = tomlrt.loads(self.input_toml)

        if not self.comment_config.header:
            document.preamble = ()
            first_key = next(iter(document), None)
            if first_key is not None and first_key in document.leading_block:
                block = document.leading_block[first_key]
                attached = _drop_orphans(block)
                if attached != block:
                    document.leading_block[first_key] = attached
        if not self.comment_config.footer:
            document.epilogue = ()

        self._filter_container_comments(document)
        self._sort_container(document, ())
        document.format(
            options=tomlrt.FormatOptions(
                indent=self.format_config.spaces_indent_inline_array,
                eol_comment_spaces=self.format_config.spaces_before_inline_comment,
                multiline_trailing_comma=(
                    self.format_config.trailing_comma_inline_array
                ),
            )
        )
        return tomlrt.dumps(document).strip() + "\n"
