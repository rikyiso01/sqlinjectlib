"""A library to simplify SQL injections during CTFs"""
from sqlinjectlib._blindinject import BlindInjector
from sqlinjectlib._databases import MySQL, DatabaseType, SQLite
from sqlinjectlib._sqlinjectlib import SQLInjector as SQLInjector, InjectorFunction
from sqlinjectlib._table import Table
from sqlinjectlib._typedql import (
    SimpleQuery,
    SQL,
    Query,
    Unknown,
    Char,
    QuerySyntaxError,
    SQLException,
)
from sqlinjectlib._unioninject import UnionInjector
from sqlinjectlib._timeinject import TimeInjector

__all__ = [
    "BlindInjector",
    "MySQL",
    "DatabaseType",
    "SQLite",
    "InjectorFunction",
    "Table",
    "SimpleQuery",
    "SQL",
    "Query",
    "Unknown",
    "Char",
    "QuerySyntaxError",
    "SQLException",
    "UnionInjector",
    "TimeInjector",
]
