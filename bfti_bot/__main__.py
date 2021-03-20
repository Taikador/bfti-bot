from discord import Game, Intents, Object

from bfti_bot.bot import Bot
from bfti_bot.config import config

# allowed_roles = [Object(id_) for id_ in config.moderation_roles]

bot = Bot(
    command_prefix=config.prefix,
    activity=Game(name=f'Commands: {config.prefix}help'),
    case_insensitive=True,
    max_messages=10_000,
    # allowed_mentions=AllowedMentions(everyone=False, roles=allowed_roles),
    intents=Intents().all(),
)
bot.run(config.token)
