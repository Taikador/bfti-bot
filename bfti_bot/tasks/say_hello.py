from logging import getLogger

from bfti_bot.bot import Bot

from ..task import DefaultScheduler, Task

log = getLogger('tasks.say_hello')


class SayHello(Task):
    def __init__(self, bot: Bot):
        self.name = 'say_hello'
        self.bot = bot

    async def run(self):
        log.info(f'Hello from {self.bot.user}')


def setup(bot: Bot):
    bot.add_task(SayHello(bot), DefaultScheduler(10.0, bot))