from discord.ext.commands import Cog, Context, command, has_any_role

from ..bot import Bot
from ..config import config


class Ping(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    @has_any_role(*config.moderation_roles)
    async def ping(self, ctx: Context):
        await ctx.send(f'Pong {ctx.author.display_name}')


def setup(bot: Bot):
    bot.add_cog(Ping(bot))
