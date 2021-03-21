# credits: https://github.com/python-discord/bot/blob/main/bot/bot.py
from __future__ import annotations

import asyncio
from contextlib import suppress
from logging import getLogger
from os import listdir
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional

import aiohttp
from discord import Guild
from discord.ext import commands
from discord.ext.commands import Cog, Command
from discord.ext.commands.errors import CheckFailure, CommandNotFound

from bfti_bot.task import Scheduler, Task

from . import logs
from .config import config

logs.setup()
log = getLogger('bot')


class Bot(commands.Bot):
    """A subclass of `discord.ext.commands.Bot` with an aiohttp session"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.extension_path: Path = Path(__file__).parent / 'extensions'
        self.task_path: Path = Path(__file__).parent / 'tasks'

        self.tasks: Dict[asyncio.Task] = {}

        # tinydb?
        self.http_session: Optional[aiohttp.ClientSession] = None
        self._guild_available = asyncio.Event()
        self.channel_available = asyncio.Event()

        self.load_extensions()
        self.load_tasks()

    def load_extensions(self) -> None:
        """Load all extensions"""

        for file in listdir(self.extension_path):
            if file.endswith('.py'):
                name = file[:-3]
                self.load_extension(
                    f'{self.extension_path.parent.name}.extensions.{name}'
                )

    def load_tasks(self) -> None:
        for file in listdir(self.task_path):
            if file.endswith('.py'):
                name = file[:-3]
                self.load_extension(f'{self.task_path.parent.name}.tasks.{name}')

    def reload_extension(self, name):
        if name.startswith('tasks.'):
            self.tasks[name].cancel()
        super().reload_extension(f'{self.extension_path.parent.name}.{name}')

    def add_cog(self, cog: Cog) -> None:
        """Adds a "cog" to the bot and logs the operation."""
        super().add_cog(cog)
        log.info(f'Cog loaded: {cog.qualified_name}')

    def remove_cog(self, name: str) -> Optional[Command]:
        super().remove_cog(name)
        log.info(f'Cog removed: {name}')

    def add_task(self, task: Task, scheduler: Scheduler):
        if not isinstance(task, Task):
            raise TypeError(f'Task "{task.name}" does not inherit from Task abc')

        self.tasks[task.name] = self.loop.create_task(scheduler.run_forever(task))
        log.info(f'Task started: {task.proper_name}')

    async def close(self) -> None:
        """Close the Discord connection and the aiohttp session"""
        # Done before super().close() to allow tasks finish before the HTTP session closes.
        for cog in list(self.cogs):
            with suppress(Exception):
                self.remove_cog(cog)

        if self.http_session:
            await self.http_session.close()

        # Now actually do full close of bot
        await super().close()
        self.loop.stop()
        self.loop.close()
        # ?????

    async def on_ready(self):
        log.info(f'Logged in as {self.user}')

        await self.wait_until_guild_available()
        log.info(
            'Now serving in guild: '
            + next(guild.name for guild in self.guilds if guild.id == config.guild_id)
        )

        self.channel = self.get_channel(config.channel_id)
        self.channel_available.set()

        app_info = await self.application_info()
        await app_info.owner.send('Bot started')

    async def on_guild_available(self, guild: Guild) -> None:
        if guild.id != config.guild_id:
            return

        self._guild_available.set()

    async def on_guild_unavailable(self, guild: Guild) -> None:
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
        log.exception(f'Unhandled exception in {event}')

    async def on_command_error(self, context, exception):
        if isinstance(exception, CheckFailure):
            log.info(f'Check failed for user {context.author}: {exception}')
        elif isinstance(exception, CommandNotFound):
            pass
        else:
            log.exception(f'Unhandled "{type(exception)}" exception: {exception}')
