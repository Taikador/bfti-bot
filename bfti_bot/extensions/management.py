from logging import getLogger

from discord.ext.commands import Cog, Context, command
from discord.ext.commands.core import is_owner

from ..bot import Bot

log = getLogger('extensions.hello')


class Management(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command(aliases=['r'])
    @is_owner()
    async def restart(self, ctx: Context):
        await ctx.message.add_reaction('✅')
        log.warn('Restarting...')

        exit(69)

    @command(name='reload-extension', aliases=('re',))
    @is_owner()
    async def reload_extension(self, ctx: Context):
        name = ctx.message.content.split()[1]
        try:
            if f'tasks.{name}' in self.bot.tasks:
                self.bot.reload_extension(f'tasks.{name}')
            else:
                self.bot.reload_extension(f'extensions.{name}')
        except Exception as exception:
            log.exception(f'Failed reloading {name}: {exception}')
            await ctx.message.add_reaction('♿')
        else:
            log.info(f'Successfully reloaded {name}')
            await ctx.message.add_reaction('✅')


def setup(bot: Bot):
    bot.add_cog(Management(bot))
