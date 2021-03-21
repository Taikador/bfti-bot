from abc import ABC, abstractmethod
from asyncio import sleep
from inspect import iscoroutinefunction

from .bot import Bot


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
    def run(self) -> None:
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, subcls):
        if cls is Task:
            return _check_methods(subcls, 'run')
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


class DefaultScheduler(Scheduler):
    def __init__(self, delay_in_s: float, bot: Bot):
        self.delay = delay_in_s
        self.bot = bot

    async def run_forever(self, task: Task) -> None:
        await self.bot.wait_until_ready()
        await self.bot.wait_until_guild_available()
        is_coro = iscoroutinefunction(task.run)

        while not self.bot.is_closed():
            if is_coro:
                await task.run()
            else:
                task.run()

            await sleep(self.delay)
