from __future__ import annotations
from collections.abc import Iterable, MutableSequence, Sequence
from typing import overload


class Table(Sequence[list[str | None]]):
    """Representation of the result of an SQL query"""

    __slots__ = ("_columns", "_tuples")

    def __init__(
        self,
        columns: MutableSequence[str],
        tuples: Iterable[MutableSequence[str | None]],
        /,
    ):
        """
        - columns: the name of the columns
        - tuples: an iterable of rows
        - raises ValueError: if the rows have a different number of elements than the columns
        """
        self._columns = tuple(columns)
        self._tuples = tuple(tuple(t) for t in tuples)
        for t in self._tuples:
            if len(t) != len(self._columns):
                raise ValueError(
                    f"Some rows don't have the right number of columns, found '{len(t)}' expected '{len(self._columns)}'"
                )

    def __len__(self) -> int:
        return len(self._tuples)

    @property
    def degree(self) -> int:
        """The number of columns"""
        return len(self._columns)

    @property
    def columns(self) -> list[str]:
        """The name of the columns"""
        return list(self._columns)

    @overload
    def __getitem__(self, item: int | str, /) -> list[str | None]:
        ...

    @overload
    def __getitem__(self, item: slice, /) -> Table:
        ...

    def __getitem__(self, item: int | slice | str, /) -> list[str | None] | Table:
        if isinstance(item, int):
            return list(self._tuples[item])
        elif isinstance(item, slice):
            return Table(list(self._columns), self)
        else:
            index = self._columns.index(item)
            return [t[index] for t in self._tuples]

    def __str__(self) -> str:
        elements = [len(t) for t in self._columns] + [
            max([len(str(k)) for k in t]) for t in self._tuples
        ]
        max_length = max(elements)
        result = "|".join(column.ljust(max_length) for column in self._columns)
        result += "\n"
        result += "-" * (max_length * len(self._columns))
        result += "\n"
        result += "\n".join(
            "|".join(str(column).ljust(max_length) for column in tuple)
            for tuple in self._tuples
        )
        return result

    def __repr__(self) -> str:
        return f"Table({self._columns}, {[[repr(elem) for elem in t] for t in self]})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Table) and other._columns == self._columns

    def __hash__(self) -> int:
        return hash((self._columns, self._tuples))
