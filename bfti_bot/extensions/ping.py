from discord.ext.commands import Cog, Context, command, has_any_role

from ..bot import Bot
from ..config import config


class Ping(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command(aliases=['p'], description='Pong game :D')
    @has_any_role(*config.moderation_roles)
    async def ping(self, ctx: Context) -> None:
        await ctx.send(
            f'Pong {ctx.message.author.mention} Your latency is: {round(self.bot.latency * 1000)} ms'
        )


def setup(bot: Bot) -> None:
    bot.add_cog(Ping(bot))
