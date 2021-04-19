import asyncio
import signal
from logging import getLogger

import uvloop
from discord import Game, Intents

from bfti_bot.bot import Bot
from bfti_bot.config import config

log = getLogger('bot')
# allowed_roles = [Object(id_) for id_ in config.moderation_roles]

uvloop.install()
loop = asyncio.get_event_loop()

bot = Bot(
    command_prefix=config.prefix,
    activity=Game(name=f'Commands: {config.prefix}help'),
    case_insensitive=True,
    max_messages=10_000,
    # allowed_mentions=AllowedMentions(everyone=False, roles=allowed_roles),
    intents=Intents().all(),
    loop=loop,
)

try:
    loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
    loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())
except NotImplementedError:
    pass

# try:
#     loop.run_until_complete(bot.start(config.token))
# except KeyboardInterrupt:
#     log.info('Received signal to terminate bot and event loop.')
# finally:
#     loop.run_until_complete(loop.shutdown_asyncgens())
#     loop.close()


async def runner():
    try:
        await bot.start(config.token)
    finally:
        if not bot.is_closed():
            await bot.close()


def stop_loop_on_completion(f):
    loop.stop()


future = asyncio.ensure_future(runner(), loop=loop)
future.add_done_callback(stop_loop_on_completion)
try:
    loop.run_forever()
except KeyboardInterrupt:
    log.info('Received signal to terminate bot and event loop.')
finally:
    future.remove_done_callback(stop_loop_on_completion)
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
