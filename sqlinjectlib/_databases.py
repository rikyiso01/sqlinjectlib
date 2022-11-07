from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from sqlinjectlib._typedql import SimpleQuery, SQL, Char, SQLType


class DatabaseType(ABC):
    """Abstract class used to build non standard SQL queries"""

    @abstractmethod
    def get_databases(self) -> SimpleQuery:
        """Creates a query to list all databases

        - returns: a SimpleQuery to list all the databases
        """
        ...

    @abstractmethod
    def get_tables(self, database: str, /) -> SimpleQuery:
        """Creates a query to list all the tables of a database

        - database: the database to list the tables
        - returns: a SimpleQuery to list all the tables in the database
        """
        ...

    @abstractmethod
    def get_columns(self, table: str, /) -> SimpleQuery:
        """Creates a query to list all the columns of a table

        - table: the table to list the columns
        - returns: a SimpleQuery to list all the columns in the table
        """
        ...

    @abstractmethod
    def ascii(self, sql: SQL[Char], /) -> SQL[int]:
        """Creates a query that converts a char into its ascii representation

        - sql: the source query
        - returns: a query that returns the ascii representation of the result of the given query
        """
        ...

    @abstractmethod
    def if_else(
        self, condition: SQL[bool], then: SQL[SQLType], otherwise: SQL[SQLType], /
    ) -> SQL[SQLType]:
        """Creates a query that returns the first value if the condition is true otherwise the second value

        - condition: the query to use for the condition
        - then: the first value
        - otherwise: the second value
        - returns: a query that returns the result of the first query if the value of the condition is true
            otherwise the result of the second query
        """
        ...

    @abstractmethod
    def sleep(self, time: SQL[int], /) -> SQL[int]:
        """Creates a query that makes the dbms sleep for the given seconds

        - time: the time to sleep
        - returns: a query that returns a value that has no meaning
        """
        ...

    def parse_columns(self, columns: list[str], /) -> list[str]:
        """Post processes the columns obtained by resolving the get_columns query

        - columns: the columns returned by the get_columns query
        - returns: the new columns
        """
        return columns

    def __repr__(self) -> str:
        """Returns a represetnation of this object

        - returns: the name of the database
        """
        return type(self).__name__


class MySQL(DatabaseType):
    """Support for MySQL specific queries"""

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
    """Support for SQLite specific queries"""

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
