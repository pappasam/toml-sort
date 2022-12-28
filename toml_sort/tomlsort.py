"""Utility functions and classes to sort toml text."""

import itertools
import re
from typing import Any, Iterable, Tuple, Union

import tomlkit
from tomlkit.api import aot, item, ws
from tomlkit.container import Container
from tomlkit.items import AoT, Comment, Item, Table, Trivia, Whitespace
from tomlkit.toml_document import TOMLDocument

__all__ = ["TomlSort"]


def clean_toml_text(input_toml: str) -> str:
    """Clean input toml, increasing the chance for beautiful output."""
    cleaned = re.sub(r"[\r\n][\r\n]{2,}", "\n\n", input_toml)
    return "\n" + cleaned.strip() + "\n"


def write_header_comment(from_doc: TOMLDocument, to_doc: TOMLDocument) -> None:
    """Write header comment from the FROM doc to the TO doc.

    Only writes comments / whitespace from the beginning of a TOML
    document. Anything from later in the document is ambiguous and
    cannot be sorted accurately.
    """
    for _, value in from_doc.body:
        if isinstance(value, Whitespace):
            to_doc.add(ws("\n"))
        elif isinstance(value, Comment):
            value.trivia.indent = ""
            to_doc.add(Comment(value.trivia))
        else:
            to_doc.add(ws("\n"))
            return


def convert_tomlkit_buggy_types(in_value: Any, parent: Any, key: str) -> Item:
    """Fix buggy items while iterating through tomlkit items.

    Iterating through tomlkit items can often be buggy; this function
    fixes it
    """
    if isinstance(in_value, bool):
        # Bool items don't have trivia and are resolved to Python's `bool`
        # https://github.com/sdispater/tomlkit/issues/119#issuecomment-955840942
        try:
            return parent.value.item(key)
        except AttributeError:
            return item(parent.value[key], parent)
    if isinstance(in_value, Item):
        return in_value
    if isinstance(in_value, Container):
        return Table(in_value, trivia=Trivia(), is_aot_element=False)
    return item(in_value, parent)


def sort_case_sensitive(value: Tuple[str, Item]) -> str:
    """Case sensitive function to pass to 'sorted' function."""
    return value[0]


def sort_case_insensitive(value: Tuple[str, Item]) -> str:
    """Case insensitive function to pass to 'sorted' function."""
    return value[0].lower()


class TomlSort:
    """API to manage sorting toml files.

    :var str input_toml: the input toml data for processing
    :var bool only_sort_tables: turns on sorting for only tables
    :var bool no_header: omit leading comments from the output
    :var callable sort_func: the sorting function to use for lists of items
    """

    def __init__(
        self,
        input_toml: str,
        only_sort_tables: bool = False,
        no_header: bool = False,
        ignore_case: bool = False,
    ) -> None:
        """Initializer."""
        self.input_toml = input_toml
        self.only_sort_tables = only_sort_tables
        self.no_header = no_header
        self.sort_func = (
            sort_case_insensitive if ignore_case else sort_case_sensitive
        )

    def sorted_children_table(
        self, parent: Union[Table, TOMLDocument]
    ) -> Iterable[Tuple[str, Item]]:
        """Get the sorted children of a table.

        NOTE: non-tables are wrapped in an item to ensure that they are, in
        fact, items. Tables and AoT's are definitely items, so the conversion
        is not necessary.
        """
        table_items = [
            (key, convert_tomlkit_buggy_types(parent[key], parent, key))
            for key in parent.keys()
        ]
        tables = (
            (key, value)
            for key, value in table_items
            if isinstance(value, (Table, AoT))
        )
        non_tables = (
            (key, value)
            for key, value in table_items
            if not isinstance(value, (Table, AoT))
        )
        non_tables_final = (
            sorted(non_tables, key=self.sort_func)
            if not self.only_sort_tables
            else non_tables
        )
        return itertools.chain(
            non_tables_final, sorted(tables, key=self.sort_func)
        )

    def toml_elements_sorted(self, original: Item) -> Item:
        """Returns a sorted item, recursing collections to their base."""
        if isinstance(original, Table):
            original.trivia.indent = "\n"
            new_table = Table(
                Container(),
                trivia=original.trivia,
                is_aot_element=original.is_aot_element(),
                is_super_table=original.is_super_table(),
            )
            for key, value in self.sorted_children_table(original):
                new_table[key] = self.toml_elements_sorted(value)
            return new_table
        if isinstance(original, AoT):
            new_aot = aot()
            for aot_item in original:
                new_aot.append(self.toml_elements_sorted(aot_item))
            return new_aot
        if isinstance(original, Item):
            original.trivia.indent = ""
            return original
        raise TypeError(
            "Invalid TOML; " + str(type(original)) + " is not an Item."
        )

    def toml_doc_sorted(self, original: TOMLDocument) -> TOMLDocument:
        """Sort a TOMLDocument."""
        sorted_document = tomlkit.document()
        if not self.no_header:
            write_header_comment(original, sorted_document)
        for key, value in self.sorted_children_table(original):
            sorted_document[key] = self.toml_elements_sorted(value)
        return sorted_document

    def sorted(self) -> str:
        """Sort a TOML string."""
        clean_toml = clean_toml_text(self.input_toml)
        toml_doc = tomlkit.parse(clean_toml)
        sorted_toml = self.toml_doc_sorted(toml_doc)
        return clean_toml_text(tomlkit.dumps(sorted_toml)).strip() + "\n"
