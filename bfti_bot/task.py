from abc import ABC, abstractmethod


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


class Task(ABC):
    @abstractmethod
    def run_once(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, subcls):
        if cls is Task:
            return _check_methods(subcls, 'run', 'run_once')
        return NotImplemented


class Scheduler(ABC):
    @abstractmethod
    async def run_forever(self, task: Task):
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, subcls):
        if cls is Task:
            return _check_methods(subcls, 'run_forever')
        return NotImplemented
