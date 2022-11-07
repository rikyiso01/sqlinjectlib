from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from sqlinject._typedql import SimpleQuery, SQL, Char, SQLType


class DatabaseType(ABC):
    @abstractmethod
    def get_databases(self) -> SimpleQuery:
        ...

    @abstractmethod
    def get_tables(self, database: str, /) -> SimpleQuery:
        ...

    @abstractmethod
    def get_columns(self, table: str, /) -> SimpleQuery:
        ...

    @abstractmethod
    def ascii(self, sql: SQL[Char], /) -> SQL[int]:
        ...

    @abstractmethod
    def if_else(
        self, condition: SQL[bool], then: SQL[SQLType], otherwise: SQL[SQLType], /
    ) -> SQL[SQLType]:
        ...

    @abstractmethod
    def sleep(self, time: SQL[int], /) -> SQL[int]:
        ...

    def parse_columns(self, columns: list[str], /) -> list[str]:
        return columns

    def __repr__(self) -> str:
        return type(self).__name__


class MySQL(DatabaseType):
    def get_databases(self) -> SimpleQuery:
        return SimpleQuery(SQL.column("schema_name"), "information_schema.schemata")

    def get_tables(self, database: str, /) -> SimpleQuery:
        return SimpleQuery(
            SQL.column("table_name"),
            "information_schema.tables",
            SQL("table_schema") @ SQL.str(database),
        )

    def get_columns(self, table: str, /) -> SimpleQuery:
        return SimpleQuery(
            SQL.column("column_name"),
            "information_schema.columns",
            SQL("table_name") @ SQL.str(table),
        )

    def ascii(self, sql: SQL[Char], /) -> SQL[int]:
        return SQL(f"ascii({sql})")

    def if_else(
        self, condition: SQL[bool], then: SQL[SQLType], otherwise: SQL[SQLType], /
    ) -> SQL[SQLType]:
        return SQL(f"if({condition},{then},{otherwise})")

    def sleep(self, time: SQL[int]) -> SQL[int]:
        return SQL(f"sleep({time})")


class SQLite(DatabaseType):
    def get_databases(self) -> SimpleQuery:
        return SimpleQuery(
            SQL.column("name"),
            "sqlite_schema",
        )

    def get_tables(self, _: str, /) -> SimpleQuery:
        return SimpleQuery(
            SQL.column("name"),
            "sqlite_schema",
        )

    def get_columns(self, table: str, /) -> SimpleQuery:
        return SimpleQuery(
            SQL.column("sql"),
            "sqlite_master",
            SQL("tbl_name") @ SQL.str(table),
        )

    def unicode(self, sql: SQL[Char], /) -> SQL[int]:
        return SQL(f"unicode({sql})")

    def ascii(self, sql: SQL[Char], /) -> SQL[int]:
        s: SQL[Any] = SQL.str("")
        return self.if_else(sql @ s, SQL.int(0), self.unicode(sql))

    def if_else(
        self, condition: SQL[bool], then: SQL[SQLType], otherwise: SQL[SQLType], /
    ) -> SQL[SQLType]:
        return SQL(f"(case when {condition} then {then} else {otherwise} end)")

    def sleep(self, _: SQL[int], /) -> SQL[int]:
        raise NotImplementedError("SQLite hasn't any sleep function")

    def parse_columns(self, columns: list[str]) -> list[str]:
        if not columns:
            return columns
        lines = columns[0].splitlines()[1:-1]
        return [line.strip().split()[0] for line in lines]
