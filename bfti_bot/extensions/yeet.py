import re
from asyncio import sleep
from logging import getLogger
from time import time
from typing import List

from discord import Guild, Member, Message, VoiceChannel
from discord.ext.commands import Cog, Context, command, has_any_role

from ..bot import Bot
from ..config import config

log = getLogger('extensions.yeet')


class Yeet(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command(
        aliases=['y'],
        usage='<user> <time in s> [<channel regex>]',
        description='Repeatly changes a users voice channel',
    )
    @has_any_role(*config.moderation_roles)
    async def yeet(self, ctx: Context) -> None:
        if not ctx.message:
            await ctx.send(ctx.command.usage)
            return
        msg: Message = ctx.message

        if len(msg.mentions) < 1:
            await ctx.send(ctx.command.usage)
            return
        target = msg.mentions[0]

        if not isinstance(target, Member):
            await ctx.send("Something wen't wrong")
            return
        target_member: Member = target

        if not target_member.voice:
            await ctx.send(f'User <@!{target_member.id}> has to be in a voice channel')
            return

        args: List[str] = ctx.message.content.split(' ')
        if len(args) < 4:
            await ctx.send(ctx.command.usage)
            return
        args = args[2:]

        if not args[0].isnumeric():
            await ctx.send(ctx.command.usage)
            return
        duration = float(args[0])

        patterns = list(
            map(
                lambda pattern: re.compile(
                    pattern if pattern.startswith('^') else '.*' + pattern,
                    flags=re.IGNORECASE,
                ),
                args[1:],
            )
        )

        if not ctx.guild:
            await ctx.send(f'User <@!{target_member.id}> has to be in a voice channel')
            return

        guild: Guild = ctx.guild  # pyright: reportGeneralTypeIssues=false

        if not guild.voice_channels:
            await ctx.send("Something wen't wrong")
            return
        channels = [
            channel
            for channel in guild.voice_channels
            if any(pattern.match(channel.name) for pattern in patterns)
        ]
        if len(channels) < 2:
            await ctx.send(ctx.command.usage)
            return

        await ctx.send(
            f'User <@!{target_member.id}> will be moved around between {[channel.name for channel in channels]} for {duration}s'
        )

        prev_channel = target_member.voice.channel
        if await self._move_around(target_member, channels, duration):
            await target_member.move_to(prev_channel)

    async def _move_around(
        self, target: Member, channels: List[VoiceChannel], duration: float
    ) -> bool:
        start = time()
        while True:
            for channel in channels:
                if time() - start > duration:
                    return True
                if not target.voice:
                    return False

                await target.move_to(channel)
                await sleep(0.6)


def setup(bot: Bot) -> None:
    bot.add_cog(Yeet(bot))
