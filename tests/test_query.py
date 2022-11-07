from sqlinject import Query, SQL, Unknown
from pytest import mark


@mark.parametrize(
    "select",
    [None, [SQL.column("5")], [SQL("5"), SQL("6")], [SQL("(1+2)"), SQL("(4+6)")]],
)
@mark.parametrize("table", [None, "test", "test.test"])
@mark.parametrize("where", [None, SQL.column("a=5")])
def test_query(
    select: list[SQL[Unknown]] | None, table: str | None, where: SQL[Unknown] | None
) -> None:
    string = f"select {'*' if select is None else ','.join(map(str,select))}"
    if table is not None:
        string += f" from {table}"
    if where is not None:
        string += f" where {where}"
    query = Query.parse(string)
    assert query.select == select
    assert query.table == table
    assert query.where == where
