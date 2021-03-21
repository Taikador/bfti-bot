from abc import ABC, abstractmethod
from functools import cache, cached_property
from pathlib import Path


def _check_methods(C, *methods):
    mro = C.__mro__
    for method in methods:
        for B in mro:
            if method in B.__dict__:
                if B.__dict__[method] is None:
                    return NotImplemented
                break
        else:
            return NotImplemented
    return True


class TaskMeta(ABC):
    async def run_once(self) -> None:
        pass

    @abstractmethod
    async def run(self) -> None:
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, subcls):
        if cls is TaskMeta:
            return _check_methods(subcls, 'run')
        return NotImplemented


class Task(TaskMeta):
    @cache
    def _get_name(self, file):
        path = Path(file)
        return 'tasks.' + path.name[: -len(path.suffix)]

    @cached_property
    def proper_name(self):
        return __class__.__name__


class Scheduler(ABC):
    @abstractmethod
    async def run_forever(self, task: Task):
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, subcls):
        if cls is Task:
            return _check_methods(subcls, 'run_forever')
        return NotImplemented
