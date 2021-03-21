from abc import ABC, abstractmethod
from functools import cache, cached_property
from pathlib import Path
from typing import Any, Union


NotImplementedType = type(NotImplemented)


def _check_methods(C, *methods) -> Union[bool, NotImplementedType]:
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
        """May be a method or coroutine"""
        pass

    @abstractmethod
    async def run(self) -> None:
        """May be a method or coroutine"""
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, subcls: Any) -> Union[bool, NotImplementedType]:
        if cls is TaskMeta:
            return _check_methods(subcls, 'run')
        return NotImplemented


class Task(TaskMeta):
    """All tasks should inherit from this class"""

    @cache
    def _get_name(self, file: str) -> str:
        path = Path(file)
        return 'tasks.' + path.name[: -len(path.suffix)]

    @cached_property
    def proper_name(self) -> str:
        return __class__.__name__


class Scheduler(ABC):
    @abstractmethod
    async def run_forever(self, task: Task) -> None:
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, subcls: Any) -> Union[bool, NotImplementedType]:
        if cls is Task:
            return _check_methods(subcls, 'run_forever')
        return NotImplemented
