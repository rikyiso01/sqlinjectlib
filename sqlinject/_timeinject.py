from __future__ import annotations
from sqlinject._sqlinject import InjectorFunction
from sqlinject._blindinject import BlindInjector
from sqlinject._databases import DatabaseType, MySQL
from sqlinject._typedql import SQL
from sqlinject._utils import wrap
from time import time


class TimeInjector(BlindInjector):
    def __init__(
        self,
        injector: InjectorFunction[SQL[int], None],
        /,
        *,
        concurrent: bool = False,
        database_type: DatabaseType = MySQL(),
        interval: int = 5,
    ):
        self.__injector = wrap(injector)
        self.__interval = interval
        super().__init__(
            self.__call, database_type=database_type, concurrent=concurrent
        )

    async def __call(self, query: SQL[bool]) -> bool:
        start = time()
        await self.__injector(
            self.database_type.if_else(
                query, self.database_type.sleep(SQL.int(self.__interval)), SQL.none()
            )
        )
        delta = time() - start
        return delta > self.__interval
