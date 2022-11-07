from __future__ import annotations
from collections.abc import Iterable, Iterator
from typing import overload


class Table:
    __slots__ = ("_columns", "_tuples")

    def __init__(self, columns: list[str], tuples: Iterable[list[str | None]], /):
        self._columns = columns.copy()
        self._tuples = [t.copy() for t in tuples]
        for t in tuples:
            if len(t) != len(self._columns):
                raise ValueError(
                    f"Some rows don't have the right number of columns, found '{len(t)}' expected '{len(self._columns)}'"
                )

    def __len__(self) -> int:
        return len(self._tuples)

    @property
    def degree(self) -> int:
        return len(self._columns)

    @overload
    def __getitem__(self, item: int | str, /) -> list[str | None]:
        ...

    @overload
    def __getitem__(self, item: slice, /) -> Table:
        ...

    def __getitem__(self, item: int | slice | str, /) -> list[str | None] | Table:
        if isinstance(item, int):
            return self._tuples[item]
        elif isinstance(item, slice):
            return Table(self._columns, self._tuples[item])
        else:
            index = self._columns.index(item)
            return [t[index] for t in self._tuples]

    def __iter__(self) -> Iterator[list[str | None]]:
        return iter([t.copy() for t in self._tuples])

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
        return f"Table({self._columns}, {[list(t) for t in self._tuples]})"
