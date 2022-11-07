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
    """Representation of a char type in an SQL query even if it doesn't exist"""

    ...


class Unknown:
    """Representation of an unknown type in an SQL query"""

    ...


class SQLException(Exception):
    """Exception related to SQL"""

    ...


class QuerySyntaxError(SQLException):
    """Exception related to a malformed SQL query"""

    ...


@dataclass(frozen=True, slots=True)
class Query:
    """Representation of a complete SQL query"""

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
    """The values of the select statement, None if 'select *'"""
    table: str | None
    """The table of the from statement, None if the from part is absent"""
    where: SQL[bool] | None = None
    """The where part of the statement, None if the where part is absent"""

    def __str__(self) -> str:
        result = f"select {'*' if self.select is None else ','.join(str(s) for s in self.select)} from {self.table}"
        if self.where is not None:
            result += f" where {self.where}"
        return result


@dataclass(frozen=True, slots=True)
class SimpleQuery:
    """Representation of a simplified SQL query without star operator and with only one column"""

    select: SQL[Any]
    """The column"""
    table: str | None = None
    """The table or None if the from part is absent"""
    where: SQL[bool] | None = None
    """The where part of the statement, None if the where part is absent"""

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
"""Possible return types of a SQL expression"""


@dataclass(frozen=True, slots=True)
class SQL(Generic[T]):
    """Representation of an SQL expression"""

    @staticmethod
    def none() -> SQL[Any]:
        """The equivalent of None in SQL

        - returns: the null expression
        """
        return SQL("null")

    @staticmethod
    def subquery(query: SimpleQuery, offset: int, /) -> SQL[Unknown]:
        """A subquery that returns a scalar value

        - query: the query to use
        - offset: the index of the element to return as a scalar
        - returns: the element at position offset of the query
        """
        return SQL(f"({query} limit 1 offset {offset})")

    @staticmethod
    def count(query: SimpleQuery, /) -> SQL[int]:
        """Count the tuples of a subquery

        - query: the query to use
        - returns: the count of tuples of the query
        """
        return SQL(f"(select count(*) from ({query}) as result)")

    @staticmethod
    def column(name: str, /) -> SQL[Unknown]:
        """Representation of a column in an SQL expression

        - name: the name of the column
        - returns: the column name
        """
        return SQL(f"{name}")

    @staticmethod
    def str(string: str | SQL[Any], /) -> SQL[str]:
        """Converts a python string or a SQL expression in an SQL string

        - string: the value to convert
        - returns: the SQL string if string is a string otherwise a SQL cast into string"""
        if isinstance(string, str):
            return SQL(f"'{string}'")
        else:
            return SQL(f"cast({string} as char)")

    @staticmethod
    def int(value: int, /) -> SQL[int]:
        """Converts a python int into a SQL integer

        - value: the value to convert
        - returns: the sql integer
        """
        return SQL(f"{value}")

    @staticmethod
    def bool(value: bool, /) -> SQL[bool]:
        """Converts a python bool into a SQL boolean

        - value: the value to convert
        - returns: the sql boolean
        """
        return SQL(f"{value}")

    @staticmethod
    def char(value: str, /) -> SQL[Char]:
        """Converts a Char literal into a SQL char

        - value: the char
        - returns: the SQL string
        - raises ValueError: if the given string longer than 1 character
        """
        if len(value) != 1:
            raise ValueError(f"'{value}' is not a char")
        return SQL(f"'{value}'")

    @staticmethod
    def coalesce(sql: SQL[T], other: SQL[T], /) -> SQL[T]:
        """Converts null into another value otherwise returns the value

        - sql: the query to convert if null
        - other: the value to use if sql is null
        - returns: a query that converts sql into other if sql is null
        """
        return SQL(f"coalesce({sql},{other})")

    query: str
    """The text of the expression"""

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
