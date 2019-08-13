"""Toml Sort

Provides a class to simply sort TOMl files
"""

import re
import itertools
from typing import Union, Iterable, Tuple, Set

import tomlkit
from tomlkit.api import aot, ws, boolean
from tomlkit.toml_document import TOMLDocument
from tomlkit.container import Container
from tomlkit.items import Item, Table, AoT, Comment, Whitespace


def clean_toml_text(input_toml: str) -> str:
    """Clean input toml, increasing the chance for beautiful output"""
    cleaned = re.sub(r"[\r\n][\r\n]{2,}", "\n\n", input_toml)
    return "\n" + cleaned.strip() + "\n"


def is_table(element: Union[Item, Container]) -> bool:
    """Determines whether a TOML element is classified as a table type"""
    return isinstance(element, (Container, Table, AoT))


def write_header_comment(from_doc: TOMLDocument, to_doc: TOMLDocument) -> None:
    """Write header comment from the FROM doc to the TO doc

    Only writes comments / whitespace from the beginning of a TOML document.
    Anything from later in the document is ambiguous and cannot be sorted
    accurately.
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


def clean_buggy_types(value: object) -> Item:
    """Clean buggy types

    Sometimes, tomlkit returns a primitive type instead of an Item. This
    function forces primitive types into Items.
    """
    if isinstance(value, bool):
        return boolean("true" if value else "false")
    return value


class TomlSort:
    """API to manage sorting toml files"""

    def __init__(
        self, input_toml: str, only_sort_tables: bool = False
    ) -> None:
        """Initializer

        :attr input_toml: the input toml data for processing
        :attr only_sort_tables: turns on sorting for only tables
        """
        self.input_toml = input_toml
        self.only_sort_tables = only_sort_tables

    def sorted_children_table(
        self, parent: Table
    ) -> Iterable[Tuple[str, Item]]:
        """Get the sorted children of a table"""
        tables = (
            (key, parent[key])
            for key in parent
            if isinstance(parent[key], (Table, AoT))
        )
        non_tables = (
            (key, clean_buggy_types(parent[key]))
            for key in parent
            if not isinstance(parent[key], (Table, AoT))
        )
        non_tables_final = (
            sorted(non_tables, key=lambda x: x[0])
            if not self.only_sort_tables
            else non_tables
        )
        return itertools.chain(
            non_tables_final, sorted(tables, key=lambda x: x[0])
        )

    def toml_elements_sorted(self, original: Item) -> Item:
        """Returns a sorted item, recursing collections to their base"""
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
            # REFACTOR WHEN POSSIBLE:
            #
            # NOTE: this section contains a necessary hack tomlkit's AoT
            # implementation currently generates duplicate elements. I rely on
            # the object id remove these duplicates, since the object id will
            # allow correct duplicates to remain
            new_aot = aot()
            id_lookup = set()  # type: Set[int]
            for aot_item in original:
                id_aot_item = id(aot_item)
                if id_aot_item not in id_lookup:
                    new_aot.append(self.toml_elements_sorted(aot_item))
                    id_lookup.add(id_aot_item)
            return new_aot
        if isinstance(original, Item):
            original.trivia.indent = ""
            return original
        raise TypeError("Invalid TOML; " + type(original) + " is not an Item")

    def toml_doc_sorted(self, original: TOMLDocument) -> TOMLDocument:
        """Sort a TOMLDocument"""
        sorted_document = tomlkit.document()
        write_header_comment(original, sorted_document)
        for key, value in self.sorted_children_table(original):
            sorted_document[key] = self.toml_elements_sorted(value)
        return sorted_document

    def sorted(self) -> str:
        """Sort a TOML string"""
        clean_toml = clean_toml_text(self.input_toml)
        toml_doc = tomlkit.parse(clean_toml)
        sorted_toml = self.toml_doc_sorted(toml_doc)
        return clean_toml_text(tomlkit.dumps(sorted_toml)).strip() + "\n"
