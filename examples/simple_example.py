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
    from time import perf_counter

    my_dag = MyDag()
    my_dag.build()

    ts = perf_counter()

    asyncio.run(my_dag.run())

    print(f"Running all tasks lasts {perf_counter() - ts:.4} seconds")
