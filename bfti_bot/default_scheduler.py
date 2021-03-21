from asyncio import sleep
from inspect import iscoroutinefunction

from .bot import Bot
from .task import Scheduler, Task


class DefaultScheduler(Scheduler):
    def __init__(self, delay_in_s: float, bot: Bot):
        self.delay = delay_in_s
        self.bot = bot

    async def run_forever(self, task: Task) -> None:
        await self.bot.wait_until_ready()
        await self.bot.wait_until_guild_available()
        is_coro = iscoroutinefunction(task.run)

        if iscoroutinefunction(task.run_once):
            await task.run_once()
        else:
            task.run_once()

        while not self.bot.is_closed():
            if is_coro:
                await task.run()
            else:
                task.run()

            await sleep(self.delay)
