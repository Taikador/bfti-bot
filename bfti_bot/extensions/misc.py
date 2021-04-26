from os import name
from discord.channel import VoiceChannel
from discord.ext.commands import Cog, Context, command, has_any_role
from discord.ext.commands.core import check
from discord.colour import Color, Colour
from discord.embeds import Embed

from ..bot import Bot
from ..config import config


def in_voice_channel():
        def predicate(ctx):
            return ctx.author.voice and ctx.author.voice.channel
        return check(predicate)

class Misc(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command(
        aliases=['p'], 
        description='Pong game :D'
        )
    @has_any_role(*config.moderation_roles)
    async def ping(self, ctx: Context) -> None:
        await ctx.send(
            f'Pong {ctx.message.author.mention} Your latency is: {round(self.bot.latency * 1000)} ms'
        )

    @in_voice_channel()
    @command(
        aliases=['m', '-',], 
        description='Move all members to your channel'
        )
    @has_any_role(*config.moderation_roles)
    async def mafk(self, ctx: Context):
        await self.bot._guild_available.wait()
        
        current_channel = ctx.author.voice.channel
        other_channels  = [channel for channel in self.bot.guild.voice_channels if not channel.id == current_channel.id]
        teacher_role    = self.bot.guild.get_role(config.teacher_role)

        for channel in other_channels:
            for member in channel.members:
                if not member.voice or teacher_role in member.roles:
                    continue
                await member.move_to(current_channel)
        await ctx.send(f'{ctx.message.author.mention} moved all members')

    @command(
        aliases=['e'],
        description='Create a custom embed',
        usage='Usage: `<author> # <title> # <message> # <date>`',
    )
    @has_any_role(*config.moderation_roles)
    async def embed(self, ctx : Context, *, content: str):
        data = content.split('#')
        if len(data) != 4:
            await ctx.send(ctx.command.usage)
            return
        author, title, message, date = data
        await ctx.message.delete()
        embed = Embed(
            title=title,
            type='rich', 
            colour=Color.dark_green(),
            )
        embed.set_author(name=author)
        embed.add_field(name='Aufgabe/Nachricht', value=message)
        embed.add_field(name='Datum', value=date)
        embed.set_footer(text=self.bot.signature)
        
        await ctx.send(embed=embed)

def setup(bot: Bot) -> None:
    bot.add_cog(Misc(bot))
