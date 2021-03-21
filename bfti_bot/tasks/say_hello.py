from datetime import datetime
from logging import getLogger
from pathlib import Path

from discord import TextChannel

from bfti_bot.bot import Bot

from ..task import Task
from ..default_scheduler import DefaultScheduler

log = getLogger('tasks.say_hello')


class SayHello(Task):
    def __init__(self, bot: Bot):
        path = Path(__file__)
        self.name = 'tasks.' + path.name[: -len(path.suffix)]
        self.proper_name = __class__.__name__
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
