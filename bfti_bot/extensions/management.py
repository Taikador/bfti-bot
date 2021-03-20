from logging import getLogger

from discord.ext.commands import Cog, Context, command, has_any_role
from discord.ext.commands.core import is_owner

from ..bot import Bot
from ..config import config

log = getLogger('extensions.hello')


class Management(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        log.info(f'Logged in as {self.bot.user}')

        await self.bot.wait_until_guild_available()
        log.info(
            'Now serving in guild: '
            + next(
                guild.name for guild in self.bot.guilds if guild.id == config.guild_id
            )
        )

        app_info = await self.bot.application_info()
        await app_info.owner.send('Bot started')

    @command()
    @has_any_role(*config.moderation_roles)
    async def ping(self, ctx: Context):
        await ctx.send(f'Pong {ctx.author.display_name}')

    @command()
    @is_owner()
    async def restart(self, ctx: Context):
        await ctx.send('Restarting...')
        log.warn('Restarting...')

        exit(69)


def setup(bot: Bot):
    bot.add_cog(Management(bot))