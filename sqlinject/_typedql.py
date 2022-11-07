from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Generic, TypeVar
from re import IGNORECASE, compile

SELECT = r"select\s+(?:\*|([^\s;]+))"

TABLE_NAME = r"[\w]+(?:.\w+)?"

FROM = rf"from\s+({TABLE_NAME})"

WHERE = r"where\s+([^\s;]+)"

QUERY_REGEX = compile(rf"{SELECT}(?:\s+{FROM})?(?:\s+{WHERE})?", IGNORECASE)


class Char:
    ...


class Unknown:
    ...


class SQLException(Exception):
    ...


class QuerySyntaxError(SQLException):
    ...


@dataclass(frozen=True, slots=True)
class Query:
    @staticmethod
    def parse(query: str, /) -> Query:
        m = QUERY_REGEX.fullmatch(query)
        if not m:
            raise QuerySyntaxError(f"Invalid query '{query}'")
        g1: str | None = m.group(1)
        g2: str | None = m.group(2)
        g3: str | None = m.group(3)
        select: list[str] | None
        if g1 is not None:
            select = g1.replace(" ", "").split(",")
        else:
            select = None
        return Query(
            [SQL(s) for s in select] if select is not None else None,
            g2,
            SQL(g3) if g3 is not None else None,
        )

    select: list[SQL[Any]] | None
    table: str | None
    where: SQL[bool] | None = None

    def __str__(self) -> str:
        result = f"select {'*' if self.select is None else ','.join(str(s) for s in self.select)} from {self.table}"
        if self.where is not None:
            result += f" where {self.where}"
        return result


@dataclass(frozen=True, slots=True)
class SimpleQuery:
    select: SQL[Any]
    table: str | None = None
    where: SQL[bool] | None = None

    def __str__(self) -> str:
        result = f"select {self.select}"
        if self.table is not None:
            result += f" from {self.table}"
        if self.where is not None:
            result += f" where {self.where}"
        return result


T = TypeVar("T", int, Char, str, bool, Unknown)
V = TypeVar("V", int, Char, str, bool, Unknown)
SQLType = TypeVar("SQLType", int, Char, str, bool, Unknown)


@dataclass(frozen=True, slots=True)
class SQL(Generic[T]):
    @staticmethod
    def none() -> SQL[Any]:
        return SQL("null")

    @staticmethod
    def subquery(query: SimpleQuery, offset: int, /) -> SQL[Unknown]:
        return SQL(f"({query} limit 1 offset {offset})")

    @staticmethod
    def count(query: SimpleQuery, /) -> SQL[int]:
        return SQL(f"(select count(*) from ({query}) as result)")

    @staticmethod
    def column(name: str, /) -> SQL[Unknown]:
        return SQL(f"{name}")

    @staticmethod
    def str(string: str | SQL[Any], /) -> SQL[str]:
        if isinstance(string, str):
            return SQL(f"'{string}'")
        else:
            return SQL(f"cast({string} as char)")

    @staticmethod
    def int(value: int, /) -> SQL[int]:
        return SQL(f"{value}")

    @staticmethod
    def bool(value: bool, /) -> SQL[bool]:
        return SQL(f"{value}")

    @staticmethod
    def char(value: str, /) -> SQL[Char]:
        """Char literal in SQL

        >>> str(SQL.char('1'))
        "'1'"
        """
        if len(value) != 1:
            raise ValueError(f"'{value}' is not a char")
        return SQL(f"'{value}'")

    @staticmethod
    def coalesce(sql: SQL[T], other: SQL[T], /) -> SQL[T]:
        return SQL(f"coalesce({sql},{other})")

    query: str

    def __str__(self) -> str:
        return self.query

    def __add__(self: SQL[int], other: SQL[int], /) -> SQL[int]:
        return SQL(f"({self}+{other})")

    def __matmul__(self: SQL[T], other: SQL[T], /) -> SQL[bool]:
        return SQL(f"({self}={other})")

    def __getitem__(self: SQL[str], index: int, /) -> SQL[Char]:
        return SQL(f"substr({self},{index+1},1)")

    def __and__(self: SQL[int], other: SQL[int], /) -> SQL[int]:
        return SQL(f"({self}&{other})")
