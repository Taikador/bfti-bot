from logging import getLogger

from discord.ext.commands import Cog, Context, command
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

    @command(aliases=['r'])
    @is_owner()
    async def restart(self, ctx: Context):
        await ctx.send('Restarting...')
        log.warn('Restarting...')

        exit(69)

    @command(name='reload-extension', aliases=('re',))
    @is_owner()
    async def reload_extension(self, ctx: Context):
        name = ctx.message.content.split()[1]
        try:
            self.bot.reload_extension(
                f'{self.bot.extension_path.parent.name}.extensions.{name}'
            )
        except Exception as exception:
            log.exception(f'Failed reloading {name}: {exception}')
            await ctx.message.add_reaction('♿')
        else:
            log.info(f'Successfully reloaded {name}')
            await ctx.message.add_reaction('✅')


def setup(bot: Bot):
    bot.add_cog(Management(bot))