"""Toml Sort

Provides a class to simply sort TOMl files
"""

import re
import itertools
from typing import Union, List, Tuple, Set

import tomlkit
from tomlkit.toml_document import TOMLDocument
from tomlkit.container import Container
from tomlkit.items import Item, Table, AoT, Trivia


def clean_input_toml(input_toml: str) -> str:
    """Clean input toml, increasing the chance for beautiful output"""
    cleaned = re.sub(r"[\r\n][\r\n]{2,}", "\n\n", input_toml)
    return "\n" + cleaned.strip() + "\n"


def is_table(element: Union[Item, Container]) -> bool:
    """Determines whether a TOML element is classified as a table type"""
    return isinstance(element, (Container, Table, AoT))


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
        self, parent: Union[Table, Container]
    ) -> List[Tuple[str, Union[Item]]]:
        """Get the sorted children of a table"""
        tables = (
            (key, parent[key])
            for key in parent
            if isinstance(parent[key], (Table, AoT, Container))
        )
        non_tables = (
            (key, parent[key])
            for key in parent
            if not isinstance(parent[key], (Table, AoT, Container))
        )
        non_tables_final = (
            sorted(non_tables, key=lambda x: x[0])
            if not self.only_sort_tables
            else non_tables
        )
        return list(
            itertools.chain(
                non_tables_final, sorted(tables, key=lambda x: x[0])
            )
        )

    def toml_elements_sorted(self, original: Union[Item, Container]) -> Item:
        """Returns a sorted item, recursing collections to their base"""
        if isinstance(original, Container):
            new_table = Table(
                Container(), Trivia(), False, is_super_table=False
            )
            for key, value in self.sorted_children_table(original):
                new_table[key] = self.toml_elements_sorted(value)
            return new_table
        if isinstance(original, Table):
            new_table = Table(
                Container(),
                Trivia(indent="\n"),
                is_aot_element=False,
                is_super_table=True,
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
            new_aot = []
            id_lookup = set()  # type: Set[int]
            for aot_item in original:
                id_aot_item = id(aot_item)
                if id_aot_item not in id_lookup:
                    new_aot.append(self.toml_elements_sorted(aot_item))
                    id_lookup.add(id_aot_item)
            return new_aot
        return original

    def toml_doc_sorted(self, original: TOMLDocument) -> TOMLDocument:
        """Sort a TOMLDocument"""
        sorted_document = tomlkit.document()
        for key, value in self.sorted_children_table(original):
            sorted_document[key] = self.toml_elements_sorted(value)
        return sorted_document

    def sorted(self) -> str:
        """Sort a TOML string"""
        clean_toml = clean_input_toml(self.input_toml)
        toml_doc = tomlkit.parse(clean_toml)
        sorted_toml = self.toml_doc_sorted(toml_doc)
        return tomlkit.dumps(sorted_toml).strip() + "\n"
