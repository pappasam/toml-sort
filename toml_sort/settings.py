"""TomlSort pyproject settings validation model."""
from typing import Optional

from pydantic import BaseModel, Extra, PositiveInt


class Settings(BaseModel):
    """Used to validate settings loaded from pyproject.toml."""

    all: Optional[bool]
    in_place: Optional[bool]
    no_header: Optional[bool]
    no_comments: Optional[bool]
    no_header_comments: Optional[bool]
    no_footer_comments: Optional[bool]
    no_inline_comments: Optional[bool]
    check: Optional[bool]
    ignore_case: Optional[bool]
    no_sort_tables: Optional[bool]
    sort_inline_tables: Optional[bool]
    sort_inline_arrays: Optional[bool]
    sort_table_keys: Optional[bool]
    spaces_before_inline_comment: Optional[PositiveInt]
    spaces_indent_inline_array: Optional[PositiveInt]
    trailing_comma_inline_array: Optional[bool]

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic model configuration."""

        extra = Extra.forbid
        frozen = True
