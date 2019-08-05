"""Toml Sort

A library to easily sort toml files.
"""

import re

from tomlkit import dumps, parse, document
from tomlkit.toml_document import TOMLDocument, Container

from tomlkit.items import (
    Trivia,
    AoT,
    Array,
    Bool,
    Comment,
    Date,
    DateTime,
    Float,
    InlineTable,
    Integer,
    Item,
    Null,
    String,
    Table,
    Time,
    Whitespace,
)


def tomlkit_sort_recursive(original: Item) -> Item:
    """Returns a sorted item, recursing collections to their base"""
    if isinstance(
        original,
        (
            Bool,
            Date,
            DateTime,
            Float,
            Integer,
            Null,
            String,
            Time,
            InlineTable,
            Array,
            AoT,
        ),
    ):
        return original
    if isinstance(original, Table):
        new_table = Table(
            Container(), Trivia(indent="\n"), False, is_super_table=True
        )
        for key in sorted(original):
            new_table[key] = tomlkit_sort_recursive(original.get(key))
        return new_table
    if isinstance(original, Container):
        new_table = Table(Container(), Trivia(), False, is_super_table=False)
        for key in sorted(original):
            new_table[key] = tomlkit_sort_recursive(original.get(key))
        return new_table
    print(type(original))
    raise ValueError("Oops, something went recursively wrong")


def tomlkit_sort(original: TOMLDocument) -> TOMLDocument:
    """Take a parsed toml document and return a sorted toml document"""
    sorted_document = document()
    for key in sorted(original):
        sorted_document[key] = tomlkit_sort_recursive(original.get(key))
    return sorted_document


def clean_input_str(instr: str) -> str:
    """Clean an input string, increasing the chance for beautiful output"""
    cleaned = re.sub(r"[\r\n][\r\n]{2,}", "\n\n", instr)
    return "\n" + cleaned.strip() + "\n"


def sort_toml(input_toml: str) -> str:
    """Take a TOML string, sort it, and return the sorted string"""
    clean_toml = clean_input_str(input_toml)
    toml_doc = parse(clean_toml)
    sorted_toml = tomlkit_sort(toml_doc)
    return dumps(sorted_toml).strip() + "\n"
