"""A library to simplify SQL injections during CTFs"""
from sqlinjectlib._blindinject import BlindInjector as BlindInjector
from sqlinjectlib._databases import (
    MySQL as MySQL,
    DatabaseType as DatabaseType,
    SQLite as SQLite,
)
from sqlinjectlib._sqlinjectlib import (
    SQLInjector as SQLInjector,
    InjectorFunction as InjectorFunction,
)
from sqlinjectlib._table import Table as Table
from sqlinjectlib._typedql import (
    SimpleQuery as SimpleQuery,
    SQL as SQL,
    Query as Query,
    Unknown as Unknown,
    Char as Char,
    QuerySyntaxError as QuerySyntaxError,
    SQLException as SQLException,
)
from sqlinjectlib._unioninject import UnionInjector as UnionInjector
from sqlinjectlib._timeinject import TimeInjector as TimeInjector
