from datetime import datetime
from logging import getLogger

from discord import TextChannel

from bfti_bot.bot import Bot

from ..config import config
from ..task import DefaultScheduler, Task

log = getLogger('tasks.say_hello')


class SayHello(Task):
    def __init__(self, bot: Bot):
        self.name = 'say_hello'
        self.bot = bot
        self.channel: TextChannel = None

    async def run_once(self) -> None:
        await self.bot.channel_available.wait()
        self.start = datetime.now()

    async def run(self):
        await self.bot.channel.send(
            f'Hello from {self.bot.user}, running for {(datetime.now() - self.start).seconds}'
        )


def setup(bot: Bot):
    bot.add_task(SayHello(bot), DefaultScheduler(10.0, bot))
