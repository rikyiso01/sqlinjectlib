from __future__ import annotations
from typing import Any, Iterator, TypeAlias
from sqlinjectlib import (
    BlindInjector,
    SQL,
    SQLInjector,
    SQLite,
    MySQL,
    DatabaseType,
    UnionInjector,
    TimeInjector,
    SimpleQuery,
)
from MySQLdb import connect as mysql_connect, Connection as MySQLConnection
from pytest import fixture, FixtureRequest
from sqlite3 import connect as sqlite_connect, Connection as SQLiteConnection
from tempfile import NamedTemporaryFile

DB: TypeAlias = "MySQLConnection | SQLiteConnection"


def mysql() -> Iterator[tuple[MySQLConnection, DatabaseType]]:
    with mysql_connect(
        host="db", port=3306, user="root", passwd="example"
    ) as connection:
        yield (connection, MySQL())


def sqlite() -> Iterator[tuple[SQLiteConnection, DatabaseType]]:
    with NamedTemporaryFile() as f:
        with sqlite_connect(f.name) as connection:
            yield (connection, SQLite())


@fixture(scope="module", params=[mysql, sqlite])
def db(request: FixtureRequest) -> Iterator[tuple[DB, DatabaseType]]:
    iterator = request.param()
    yield next(iterator)
    try:
        next(iterator)
    except StopIteration:
        pass


def exec(db: DB, query: str) -> list[list[Any]]:
    if isinstance(db, SQLiteConnection):
        cursor = db.cursor()
        result = cursor.execute(query).fetchall()
        cursor.close()
    else:
        db.query(query)
        cursor = db.store_result()
        result = cursor.fetch_row()
    return [list(row) for row in result]


def blind_injector(db: DB, type: DatabaseType) -> BlindInjector:
    def inject(sql: SQL[bool]) -> bool:
        return exec(db, f"select 1 where {sql}") == [[1]]

    return BlindInjector(inject, database_type=type)


def union_injector(db: DB, type: DatabaseType) -> UnionInjector:
    def inject(sql: SQL[str]) -> str | None:
        return exec(db, f"select {sql}")[0][0]

    return UnionInjector(inject, database_type=type)


def base_injector(db: DB, type: DatabaseType) -> SQLInjector:
    def inject(sql: SimpleQuery) -> list[str | None]:
        return [str(row[0]) for row in exec(db, str(sql))]

    return SQLInjector(inject, database_type=type)


def time_injector(db: DB, type: DatabaseType):
    def inject(sql: SQL[int]) -> None:
        if not isinstance(db, SQLiteConnection):
            exec(db, f"select {sql}")

    return TimeInjector(inject, database_type=type, interval=1)


@fixture(
    scope="module",
    params=[blind_injector, union_injector, base_injector, time_injector],
)
def injector(request: FixtureRequest, db: tuple[DB, DatabaseType]) -> SQLInjector:
    return request.param(db[0], db[1])


async def test_injector(injector: SQLInjector):
    if isinstance(injector.database_type, SQLite) and isinstance(
        injector, TimeInjector
    ):
        return
    async for name, value in injector.test():
        assert value, f"{injector}: {name}"
