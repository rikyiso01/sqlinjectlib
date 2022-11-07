from typing import TypeGuard, TypeVar, cast
from typing_extensions import TypeVarTuple, Unpack
from collections.abc import Callable, Awaitable

RED = "\u001b[31m"
GREEN = "\u001b[32m"
RESET = "\u001b[0m"

PASSED = f"{GREEN}ok{RESET}"
FAILED = f"{RED}error{RESET}"

T = TypeVarTuple("T")
V = TypeVar("V")
V2 = TypeVar("V2")


def print_test_result(name: str, result: bool, /) -> None:
    print(f"{name}: {PASSED if result else FAILED}")


def list_is_not_none(l: list[V | None]) -> TypeGuard[list[V]]:
    return all(elem is not None for elem in l)


def wrap(
    function: Callable[[Unpack[T]], V | Awaitable[V]]
) -> Callable[[Unpack[T]], Awaitable[V]]:
    async def result(*args: Unpack[T]) -> V:
        result = function(*args)
        if isinstance(result, Awaitable):
            return await cast(Awaitable[V], result)
        return result

    return result
