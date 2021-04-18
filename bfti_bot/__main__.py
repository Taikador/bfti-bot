import asyncio
from discord import Game, Intents
import uvloop
from logging import getLogger

from bfti_bot.bot import Bot
from bfti_bot.config import config

log = getLogger('bot')
# allowed_roles = [Object(id_) for id_ in config.moderation_roles]

bot = Bot(
    command_prefix=config.prefix,
    activity=Game(name=f'Commands: {config.prefix}help'),
    case_insensitive=True,
    max_messages=10_000,
    # allowed_mentions=AllowedMentions(everyone=False, roles=allowed_roles),
    intents=Intents().all(),
)

uvloop.install()

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(bot.start(config.token))
except KeyboardInterrupt:
    log.info('Received signal to terminate bot and event loop.')
finally:
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
