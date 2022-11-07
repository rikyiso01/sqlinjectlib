from __future__ import annotations
from argparse import ArgumentParser
from asyncio import run
from sys import stderr
from time import time
from sqlinjectlib._typedql import (
    SimpleQuery,
    Query,
    SQL,
    QuerySyntaxError,
    SQLException,
    TABLE_NAME,
)
from sqlinjectlib._table import Table
from sqlinjectlib._databases import DatabaseType, MySQL
from typing import Any, Literal, NoReturn, TypeVar, overload
from re import compile
from collections.abc import Callable, AsyncGenerator, Awaitable
from sqlinjectlib._utils import wrap, print_test_result, list_is_not_none
from importlib import import_module

HELP_REGEX = compile(r"help")
LIST_DATABASES_REGEX = compile(r"list")
LIST_TABLES_REGEX = compile(rf"list\s+(\w+)")
LIST_COLUMNS_REGEX = compile(rf"columns\s+({TABLE_NAME})")
EXIT = compile(r"exit")

T = TypeVar("T")
V = TypeVar("V")

InjectorFunction = Callable[[T], V | Awaitable[V]]
"""Generic type of a function that takes a type and can return an awaitable or a result"""


class SQLInjector:
    """Basic SQL injection

    You have a basic SQL injection when you can inject an SQL query that prints a single column
    """

    def __init__(
        self,
        injector: InjectorFunction[SimpleQuery, list[str | None]],
        *,
        database_type: DatabaseType = MySQL(),
    ):
        """
        - injector: function that given a query over a single column returns the list of values
        - database_type: the type of the database you are injecting into
        """
        self.__database_type: DatabaseType = database_type
        self.__injector = wrap(injector)

    @property
    def database_type(self) -> DatabaseType:
        """Getter for the database type

        - returns: the database type
        """
        return self.__database_type

    async def list_databases(self) -> list[str]:
        """List all databases in the dbms

        - returns: a list containing all the name of the databases"""
        result = await self.query(self.database_type.get_databases())
        if not list_is_not_none(result):
            raise ValueError("Some database names are null")
        return result

    async def list_tables(self, database: str, /) -> list[str]:
        """List all the tables in the given database

        - database: the database to get the tables from
        - returns: a list containing all the name of the tables in the database
        """
        result = await self.query(self.database_type.get_tables(database))
        if not list_is_not_none(result):
            raise ValueError(f"Some table names are null for '{database}'")
        return result

    async def list_columns(self, table: str, /) -> list[str]:
        """List all the columns in a table

        - table: the table to list the columns
        - returns: a list containing all the name of the columns in the table
        """
        result = await self.query(self.database_type.get_columns(table))
        if not list_is_not_none(result):
            raise ValueError(f"Some column names are null for '{table}'")
        result = self.database_type.parse_columns(result)
        return result

    @overload
    async def query(self, query: SimpleQuery, /) -> list[str | None]:
        ...

    @overload
    async def query(self, query: Query | str, /) -> Table:
        ...

    async def query(
        self, query: SimpleQuery | Query | str, /
    ) -> Table | list[str | None]:
        """Perform a query in the attacked database

        - query: the query to use
        - returns: a list of values of the column if the query is a SimpleQuery,
            a table if the query is a Query or a string containing the query
        - raises QuerySyntaxError: if the query is malformed
        """
        if isinstance(query, SimpleQuery):
            return await self.__injector(query)
        if isinstance(query, str):
            query = Query.parse(query)
        if query.select is None:
            if query.table is None:
                raise QuerySyntaxError(
                    f"You can't select all from a non table '{query}'"
                )
            columns = await self.list_columns(query.table)
            query = Query(
                [SQL.column(c) for c in columns],
                query.table,
                query.where,
            )
        assert query.select is not None
        tuples: list[list[str | None]] = []
        for s in query.select:
            t = await self.__injector(SimpleQuery(s, query.table, query.where))
            if len(tuples) != len(t):
                if len(tuples) == 0:
                    tuples = [[] for _ in t]
                else:
                    t = ["" for _ in tuples]
            for row, elem in zip(tuples, t):
                row.append(elem)
        return Table([str(q) for q in query.select], tuples)

    async def test(self) -> AsyncGenerator[tuple[str, bool], None]:
        """Tests if the injector gives the correct values

        - returns: an iterable of name result for each test
        """
        try:
            r = await self.__injector(SimpleQuery(SQL.int(1), None, None))
            result = len(r) == 1 and r[0] == "1"
        except:
            result = False
        yield ("working", result)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.database_type})"

    def main(self, main_function: Callable[[], Any] = lambda: exit(1), /) -> NoReturn:
        main(self, main_function)


def main(injector: SQLInjector, main: Callable[[], Any]) -> NoReturn:
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "interactive", help="start an interactive session, the default"
    )
    subparsers.add_parser("test", help="test the injector")
    subparsers.add_parser(
        "main", help="execute the passed main function, it defaults to exit(1)"
    )
    exec_parser = subparsers.add_parser("exec", help="execute the given sql query")
    exec_parser.add_argument("sql_query", nargs="+", help="the sql query to execute")
    args = vars(parser.parse_args())
    command: Literal["interactive", "test", "main", "exec"] = (
        args["command"] if args["command"] is not None else "interactive"
    )
    sql_query: list[str] = args["sql_query"] if "sql_query" in args else []
    if sql_query:
        function = exec(injector, " ".join(sql_query))
    elif command == "interactive":
        function = interactive(injector)
    elif command == "test":
        function = test(injector)
    else:
        function = main_function(main)
    run(function)
    exit()


async def exec(injector: SQLInjector, query: str) -> None:
    print(await injector.query(query))


async def test(injector: SQLInjector) -> None:
    async for test, result in injector.test():
        print_test_result(test, result)


async def main_function(main_function: Callable[[], Any]) -> None:
    await wrap(main_function)()


async def interactive(injector: SQLInjector) -> None:
    import_module("readline")
    print("Type 'help' for a list of special commands")
    while True:
        try:
            line = input("> ").strip()
            start = time()
            if LIST_DATABASES_REGEX.fullmatch(line):
                for d in await injector.list_databases():
                    print(d)
            elif EXIT.fullmatch(line):
                break
            elif match := LIST_TABLES_REGEX.fullmatch(line):
                for t in await injector.list_tables(match.group(1)):
                    print(t)
            elif match := LIST_COLUMNS_REGEX.fullmatch(line):
                for c in await injector.list_columns(match.group(1)):
                    print(c)
            elif HELP_REGEX.fullmatch(line):
                print("Special commands:")
                print("- list: list all databases")
                print("- list [database]: list all tables of database")
                print("- columns [table]: list all columns of table")
                print("- exit: exit the program")
                continue
            else:
                print(await injector.query(line))
            print("Operation took", time() - start)
        except (SQLException) as e:
            print(type(e).__name__, ":", e, file=stderr)
        except (EOFError, KeyboardInterrupt):
            exit()
