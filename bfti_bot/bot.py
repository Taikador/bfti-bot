# credits: https://github.com/python-discord/bot/blob/main/bot/bot.py
import asyncio
from contextlib import suppress
from logging import getLogger
from os import listdir
from pathlib import Path
from typing import Optional

import aiohttp
from discord import Guild
from discord.ext import commands
from discord.ext.commands import Cog, Command
from discord.ext.commands.errors import CheckFailure, MissingAnyRole

from . import logs
from .config import config

logs.setup()
log = getLogger('bot')


class Bot(commands.Bot):
    """A subclass of `discord.ext.commands.Bot` with an aiohttp session"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.extension_path: Path = Path(__file__).parent / 'extensions'

        # tinydb?
        self.http_session: Optional[aiohttp.ClientSession] = None
        self._guild_available = asyncio.Event()

        self.load_extensions()

    def load_extensions(self) -> None:
        """Load all extensions"""

        for file in listdir(self.extension_path):
            if file.endswith('.py'):
                name = file[:-3]
                self.load_extension(
                    f'{self.extension_path.parent.name}.extensions.{name}'
                )

    def add_cog(self, cog: Cog) -> None:
        """Adds a "cog" to the bot and logs the operation."""
        super().add_cog(cog)
        log.info(f'Cog loaded: {cog.qualified_name}')

    def remove_cog(self, name: str) -> Optional[Command]:
        cog = super().remove_cog(name)
        log.info(f'Cog removed: {cog.qualified_name}')

    async def close(self) -> None:
        """Close the Discord connection and the aiohttp session"""
        # Done before super().close() to allow tasks finish before the HTTP session closes.
        for cog in list(self.cogs):
            with suppress(Exception):
                self.remove_cog(cog)

        if self.http_session:
            await self.http_session.close()

        self.loop.close()
        # Now actually do full close of bot
        await super().close()

    async def on_guild_available(self, guild: Guild) -> None:
        """
        Set the internal guild available event when `config.guild_id` becomes available.
        """
        if guild.id != config.guild_id:
            return

        self._guild_available.set()

    async def on_guild_unavailable(self, guild: Guild) -> None:
        """Clear the internal guild available event when `config.guild_id` becomes unavailable."""
        if guild.id != config.guild_id:
            return

        self._guild_available.clear()

    async def wait_until_guild_available(self) -> None:
        """
        Wait until the `config.guild_id` guild is available (and the cache is ready).
        The on_ready event is inadequate because it only waits 2 seconds for a GUILD_CREATE
        gateway event before giving up and thus not populating the cache for unavailable guilds.
        """
        await self._guild_available.wait()

    async def on_error(self, event: str, *args, **kwargs) -> None:
        """Log errors raised in event listeners rather than printing them to stderr."""
        log.exception(f'Unhandled exception in {event}')

    async def on_command_error(self, context, exception):
        if isinstance(exception, CheckFailure):
            log.info(f'Check failed for user {context.author}: ^^{exception}')
        else:
            log.exception(f'Unhandled exception: {exception}')