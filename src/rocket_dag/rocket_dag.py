import asyncio
import inspect

from logging import getLogger
from collections import defaultdict
from functools import wraps


logger = getLogger(__name__)


def task(*, dependencies=[]):
    def decorator(func):

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            task_name = func.__name__
            try:
                await func(self, *args, **kwargs)
            except Exception as e:
                self.errors[task_name] = str(e)
                self.stop_dependent_tasks(task_name)
                raise e
            finally:
                self.running_tasks.discard(task_name)

        setattr(wrapper, '_task_name', func.__name__)
        setattr(wrapper, '_task_dependencies', dependencies)

        return wrapper

    return decorator

class RocketDag:
    def __init__(self):
        self.tasks = {}
        self.errors = {}
        self.running_tasks = set()  # Store running tasks

    def stop_dependent_tasks(self, error_task_name):
        visited = set()

        def dfs(task_name):
            if task_name not in visited:
                visited.add(task_name)
                for dependent_task_name in self.tasks[task_name]['dependencies']:
                    self.errors[dependent_task_name] = "Dependency error"
                    dfs(dependent_task_name)

        dfs(error_task_name)

    def build(self):
        for _, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, '__wrapped__'):
                # Check if the method is wrapped by the @task decorator
                self._add_task_from_method(method)

    def _add_task_from_method(self, method):
        task_name = method.__name__
        dependencies = getattr(method, '_task_dependencies', [])
        self.tasks[task_name] = {
            'func': method,
            'dependencies': set(dependencies)
        }

    async def run_task(self, task_name: str):
        try:
            await self.tasks[task_name]['func']()

            for task in self.tasks:
                if task_name in self.tasks[task]['dependencies']:
                    self.tasks[task]['dependencies'].remove(task_name)
        except Exception as e:
            self.errors[task_name] = str(e)
            self.stop_dependent_tasks(task_name)
            raise e
        finally:
            self.running_tasks.discard(task_name)
            del self.tasks[task_name]

    async def run(self):
        while self.tasks or self.running_tasks:
            logger.info("Running Tasks: %s" % self.running_tasks)

            entry_points = [task_name for task_name, dependencies in self.tasks.items() if not dependencies['dependencies']]
            if not entry_points:
                raise Exception("Dependency cycle detected. Cannot proceed.")

            # Start available tasks
            for task_name in entry_points:
                if task_name not in self.running_tasks:
                    self.running_tasks.add(task_name)
                    asyncio.create_task(self.run_task(task_name))

            # Sleep briefly to avoid busy-waiting
            await asyncio.sleep(0.01)
