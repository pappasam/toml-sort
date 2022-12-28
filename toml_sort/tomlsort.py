"""Utility functions and classes to sort toml text."""
from __future__ import annotations

import itertools
import re
from dataclasses import dataclass, field
from typing import Any, Iterable, List, Optional, Tuple, TypeVar, cast

import tomlkit
from tomlkit.api import item as tomlkit_item
from tomlkit.api import ws
from tomlkit.container import Container
from tomlkit.items import AoT, Comment, Item, Key, Table, Trivia, Whitespace
from tomlkit.toml_document import TOMLDocument

__all__ = ["TomlSort"]


def clean_toml_text(input_toml: str) -> str:
    """Clean input toml, increasing the chance for beautiful output."""
    cleaned = re.sub(r"[\r\n][\r\n]{2,}", "\n\n", input_toml)
    return "\n" + cleaned.strip() + "\n"


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
            return tomlkit_item(parent.value[key], parent)
    if isinstance(in_value, Item):
        return in_value
    if isinstance(in_value, Container):
        return Table(in_value, trivia=Trivia(), is_aot_element=False)
    return tomlkit_item(in_value, parent)


def sort_case_sensitive(value: TomlSortItem) -> str:
    """Case sensitive function to pass to 'sorted' function."""
    return value.key.key


def sort_case_insensitive(value: TomlSortItem) -> str:
    """Case insensitive function to pass to 'sorted' function."""
    return value.key.key.lower()


def attach_comments(item: TomlSortItem, previous_item: Table | TOMLDocument):
    """Attach the comments on item to the previous item, making sure that the
    formatting is correct for tables."""
    if item.attached_comments and isinstance(item.value, Table):
        previous_item.add(Whitespace("\n"))
        item.value.trivia.indent = ""
    for comment in item.attached_comments:
        previous_item.add(comment)


T = TypeVar("T", bound=Item)


def normalize_trivia(
    item: T, include_comments: bool = True, comment_spaces: int = 2
) -> T:
    """Normalize the trivia on an item, making sure that the indent is not set,
    and that if it has a comment, the comment is correctly formatted."""
    if not isinstance(item, Whitespace):
        trivia = item.trivia
        trivia.indent = ""
        trivia.trail = "\n"
        if trivia.comment != "":
            if include_comments:
                trivia.comment_ws = " " * comment_spaces
                trivia.comment = f"# {trivia.comment[1:].strip()}"
            else:
                trivia.comment = ""
                trivia.comment_ws = ""

    return item


def coalesce_tables(
    tables: Iterable[TomlSortItem],
) -> Iterable[TomlSortItem]:
    """Merge any duplicate keys that exist in an iterable of TomlSortItem."""
    coalesced = {}
    for table in tables:
        if table.key not in coalesced:
            coalesced[table.key] = table
        else:
            existing = coalesced[table.key]
            existing.children.extend(table.children)
            existing.attached_comments.extend(table.attached_comments)

            if isinstance(existing.value, Table):
                if existing.value.is_super_table():
                    existing.value = table.value

    return coalesced.values()


@dataclass
class TomlSortItem:
    """Dataclass used to keep track of comments attached to Toml Items while
    they are being sorted."""

    key: Key
    value: Item
    attached_comments: List[Comment] = field(default_factory=list)
    children: List[TomlSortItem] = field(default_factory=list)

    @property
    def is_table(self) -> bool:
        """Returns true if the Item inside this TomlSortItem is a Table."""
        return isinstance(self.value, Table)

    @property
    def is_super_table(self) -> bool:
        """Returns true if the Item inside this TomlSortItem is a Super
        Table."""
        return (  # pylint: disable=no-member
            self.is_table and cast(Table, self.value).is_super_table()
        )

    @property
    def table(self) -> Table:
        """Returns TomlSortItem.value if it is a Table, or a TypeError
        otherwise."""
        if not self.is_table:
            raise TypeError(
                f"self.value is {str(type(self.value))} not a Table"
            )
        return cast(Table, self.value)

    @property
    def is_aot(self) -> bool:
        """Returns true if the Item inside this TomlSortItem is an AoT."""
        return isinstance(self.value, AoT)

    @property
    def aot(self) -> AoT:
        """Returns TomlSortItem.value if it is an AoT, or a TypeError
        otherwise."""
        if not self.is_aot:
            raise TypeError(
                f"self.value is {str(type(self.value))} not an AoT"
            )

        return cast(AoT, self.value)


@dataclass
class CommentConfiguration:
    """Configures how TomlSort handles comments."""

    header: bool = True
    footer: bool = True
    end_of_line: bool = True
    inline_attached: bool = True
    spaces_before_comment: int = 2


class TomlSort:
    """API to manage sorting toml files."""

    def __init__(
        self,
        input_toml: str,
        only_sort_tables: bool = False,
        ignore_case: bool = False,
        comment_config: CommentConfiguration = None,
    ) -> None:
        """Initializer."""
        self.input_toml = input_toml
        self.only_sort_tables = only_sort_tables
        self.sort_func = (
            sort_case_insensitive if ignore_case else sort_case_sensitive
        )
        if comment_config is None:
            comment_config = CommentConfiguration()
        self.comment_config = comment_config

    def sorted_children_table(
        self, parent: List[TomlSortItem]
    ) -> Iterable[TomlSortItem]:
        """Get the sorted children of a table."""
        tables = coalesce_tables(
            item for item in parent if isinstance(item.value, (Table, AoT))
        )
        non_tables = (
            item for item in parent if not isinstance(item.value, (Table, AoT))
        )
        non_tables_final = (
            sorted(non_tables, key=self.sort_func)
            if not self.only_sort_tables
            else non_tables
        )
        return itertools.chain(
            non_tables_final, sorted(tables, key=self.sort_func)
        )

    def write_header_comment(
        self,
        from_doc_body: List[Tuple[Optional[Key], Item]],
        to_doc: TOMLDocument,
    ) -> None:
        """Write header comment from the FROM doc to the TO doc.

        Only writes comments / whitespace from the beginning of a TOML
        document. Anything from later in the document is ambiguous and
        cannot be sorted accurately.
        """
        for _, value in from_doc_body:
            if isinstance(value, Comment):
                value = normalize_trivia(
                    value,
                    comment_spaces=self.comment_config.spaces_before_comment,
                )
                to_doc.add(value)
            else:
                to_doc.add(ws("\n"))
                return

    def toml_elements_sorted(
        self, original: TomlSortItem, parent: Table | TOMLDocument
    ) -> Item:
        """Returns a sorted item, recursing collections to their base."""
        if original.is_table:
            new_table = original.table

            for item in self.sorted_children_table(original.children):
                previous_item = self.table_previous_item(new_table, parent)
                attach_comments(item, previous_item)
                new_table.add(
                    item.key, self.toml_elements_sorted(item, previous_item)
                )
            return new_table

        if original.is_aot:
            new_aot = normalize_trivia(
                original.aot,
                self.comment_config.end_of_line,
                self.comment_config.spaces_before_comment,
            )
            for table in original.children:
                previous_item = next(iter(new_aot), parent)
                attach_comments(table, previous_item)
                new_aot.append(
                    self.toml_elements_sorted(
                        table, next(iter(new_aot), previous_item)
                    )
                )

            return new_aot

        return original.value

    @staticmethod
    def table_previous_item(parent_table, grandparent):
        """Finds the previous item that we should attach a comment to, in the
        case where the previous item is a table.

        This take into account that a table may be a super table.
        """
        if parent_table.is_super_table():
            if len(parent_table) == 0:
                previous_item = grandparent
            else:
                last_item = parent_table.value.last_item()
                if last_item is None or not isinstance(last_item, Table):
                    type_str = str(type(last_item))
                    raise TypeError(
                        f"Unexpected type {type_str}, cannot insert comment."
                    )
                previous_item = last_item
        else:
            previous_item = parent_table
        return previous_item

    def body_to_tomlsortitems(
        self, parent: List[Tuple[Optional[Key], Item]]
    ) -> Tuple[List[TomlSortItem], List[Comment]]:
        """Iterate over Container.body, recursing down into sub-containers
        attaching the comments that are found to the correct TomlSortItem. We
        need to do this iteration because TomlKit puts comments into end of the
        collection they appear in, instead of the start of the next collection.

        For example:
        [xyz]

        # Comment
        [abc]

        TomlKit would place the comment from the example into the [xyz]
        collection, when we would like it to be attached to the [abc]
        collection.

        So before sorting we have to iterated over the container, correctly
        attaching the comments, then undo this process once everything is
        sorted.
        """
        items: List[TomlSortItem] = []
        comments: List[Comment] = []
        for key, value in parent:
            if key is None:
                if isinstance(value, Whitespace):
                    comments = []
                elif (
                    isinstance(value, Comment)
                    and self.comment_config.inline_attached
                ):
                    comment_spaces = self.comment_config.spaces_before_comment
                    value = normalize_trivia(
                        value,
                        comment_spaces=comment_spaces,
                    )
                    comments.append(value)
                continue

            value = convert_tomlkit_buggy_types(value, parent, key.key)
            value = normalize_trivia(
                value,
                self.comment_config.end_of_line,
                comment_spaces=self.comment_config.spaces_before_comment,
            )

            if isinstance(value, Table):
                comments, item = self.table_to_tomlsortitem(
                    comments, key, value
                )

            elif isinstance(value, AoT):
                comments, item = self.aot_to_tomlsortitem(comments, key, value)

            elif isinstance(value, Item):
                item = TomlSortItem(key, value, comments)
                comments = []

            else:
                raise TypeError(
                    "Invalid TOML; " + str(type(value)) + " is not an Item."
                )

            items.append(item)

        return items, comments

    def aot_to_tomlsortitem(
        self, comments: List[Comment], key: Key, value: AoT
    ) -> Tuple[List[Comment], TomlSortItem]:
        """Turn an AoT into a TomlSortItem, recursing down through its
        collections and attaching all the comments to the correct items."""
        new_aot = AoT([], parsed=True)
        children = []
        for table in value.body:
            [first_child], trailing_comments = self.body_to_tomlsortitems(
                [(key, table)]
            )
            first_child.attached_comments = comments
            comments = trailing_comments
            children.append(first_child)
        item = TomlSortItem(key, new_aot, children=children)
        return comments, item

    def table_to_tomlsortitem(
        self, comments: List[Comment], key: Key, value: Table
    ) -> Tuple[List[Comment], TomlSortItem]:
        """Turn a table into a TomlSortItem, recursing down through its
        collections and attaching all the comments to the correct items."""
        children, trailing_comments = self.body_to_tomlsortitems(
            value.value.body
        )
        new_table = Table(
            Container(parsed=True),
            trivia=value.trivia,
            is_aot_element=value.is_aot_element(),
            is_super_table=value.is_super_table(),
        )
        if not value.is_super_table():
            new_table.trivia.indent = "\n"

        first_child = next(iter(children), None)

        # If the first child of this item is an AoT, we want the
        # comment to be attached to the first table within the AoT,
        # rather than the parent AoT object
        if first_child and first_child.is_aot:
            first_child.children[0].attached_comments = comments
            comments = []

        # If this item is a super table we want to walk down
        # the tree and attach the comment to the first non-super table.
        if value.is_super_table():
            child_table = children[0]
            while child_table.is_super_table:
                child_table = child_table.children[0]

            child_table.attached_comments = comments
            comments = []

        item = TomlSortItem(key, new_table, comments, children)
        comments = trailing_comments
        return comments, item

    def toml_doc_sorted(self, original: TOMLDocument) -> TOMLDocument:
        """Sort a TOMLDocument."""
        sorted_document = TOMLDocument(parsed=True)

        if self.comment_config.header:
            self.write_header_comment(original.body[1:], sorted_document)

        items, footer_comment = self.body_to_tomlsortitems(original.body)

        for item in self.sorted_children_table(items):
            attach_comments(item, sorted_document)
            sorted_document.add(
                item.key, self.toml_elements_sorted(item, sorted_document)
            )

        if self.comment_config.footer and footer_comment:
            sorted_document.add(Whitespace("\n"))
            for comment in footer_comment:
                sorted_document.add(comment)

        return sorted_document

    def sorted(self) -> str:
        """Sort a TOML string."""
        clean_toml = clean_toml_text(self.input_toml)
        toml_doc = tomlkit.parse(clean_toml)
        sorted_toml = self.toml_doc_sorted(toml_doc)
        return clean_toml_text(tomlkit.dumps(sorted_toml)).strip() + "\n"
