"""TomlSort pyproject settings validation model."""
from __future__ import annotations

from pydantic import BaseModel, Extra, PositiveInt


class TomlSortSettings(BaseModel):
    """Used to validate settings loaded from pyproject.toml."""

    all: None | bool
    in_place: None | bool
    no_header: None | bool
    no_comments: None | bool
    no_header_comments: None | bool
    no_footer_comments: None | bool
    no_inline_comments: None | bool
    check: None | bool
    ignore_case: None | bool
    no_sort_tables: None | bool
    sort_inline_tables: None | bool
    sort_inline_arrays: None | bool
    sort_table_keys: None | bool
    spaces_before_inline_comment: None | PositiveInt
    spaces_indent_inline_array: None | PositiveInt
    trailing_comma_inline_array: None | bool

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic model configuration."""

        extra = Extra.forbid
        frozen = True
