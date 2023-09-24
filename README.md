# rocket-dag

[![PyPI - Version](https://img.shields.io/pypi/v/rocket-dag.svg)](https://pypi.org/project/rocket-dag)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rocket-dag.svg)](https://pypi.org/project/rocket-dag)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install rocket-dag
```

## Usage

To define a DAG of task, simply create a class from `RocketDag` and its associated `task` like the example below

```python
import asyncio

from rocket_dag import RocketDag, task


class MyDag(RocketDag):
    def __init__(self):
        super().__init__()

    @task(dependencies=['task_c'])
    async def task_a(self):
        await asyncio.sleep(0.5)
        print("hello from a")

    @task(dependencies=['task_c', 'task_a'])
    async def task_b(self):
        await asyncio.sleep(1.5)
        print("hello from b")

    @task()
    async def task_c(self):
        await asyncio.sleep(0.25)
        print("hello from task C")

    @task()
    async def task_d(self):
        await asyncio.sleep(4)
        print("Hello from D")

    @task(dependencies=['task_b'])
    async def task_e(self):
        await asyncio.sleep(3)
        print("Hello from E")

if __name__ == "__main__":
    my_dag = MyDag()

    my_dag.build()

    asyncio.run(my_dag.run())

# The code will print the following messages:
# > hello from task C
# > hello from a
# > hello from b
# > hello from D
# > hello from E
# Running all the tasks will last approximately 5.25 seconds.
```
