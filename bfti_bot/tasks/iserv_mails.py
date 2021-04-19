import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import timedelta, datetime, date
from hashlib import sha1
from imap_tools import MailBox, AND, MailMessage
from logging import getLogger
from threading import Lock
from typing import List

from discord.colour import Colour
from discord.embeds import Embed

from bfti_bot.bot import Bot
from ..background_task import DefaultScheduler, Task
from ..config import config

log = getLogger('tasks.iserv_mails')

class IservMails(Task):
    def __init__(self, bot: Bot):
        self.name = self._get_name(__file__)
        self.bot = bot

        self.shown_mails = self.bot.db.table('shown_mails')
        self.mailbox = None
        self.mail_date_within = timedelta(weeks=1)

        self.executor = ThreadPoolExecutor(1)
        self.loop = asyncio.get_event_loop()

    async def run_once(self) -> None:
        await self.loop.run_in_executor(self.executor, self._init_mailbox)
        await self.bot.channel_available.wait()

    async def run(self) -> None:
        mails = await self.loop.run_in_executor(self.executor, self._get_mails)

        shown_mail_uids = [elem['uid'] for elem in self.shown_mails.all()]
        not_shown_mails = [
            mail for mail in mails
            if mail.uid not in shown_mail_uids
        ]
        for mail in not_shown_mails:
            self.shown_mails.insert({
                'uid': mail.uid
            })

        for mail in not_shown_mails:
            embed = await self._generate_embed(mail)
            await self.bot.channel.send(content='@everyone', embed=embed)

    def _cut_mail_text(self, text: str) -> str:
        if len(text.encode('utf-8')) > 5990:
            b = text.encode('utf-8')
            return b[:5990].decode('utf-8') + '...'
        elif len(text) > 1020:
            return text[:1020] + '...'
        else:
            return text

    async def _generate_embed(self, mail: MailMessage) -> Embed:
        embed = Embed(
            title = mail.subject,
            type='rich',
            colour=Colour.dark_magenta(),
            url=f'https://bbs2celle.eu/iserv/mail?path=INBOX&msg={mail.uid}'
        )

        text = self._cut_mail_text(mail.text)

        embed.set_author(name=mail.from_)
        embed.add_field(
            name='Nachricht',
            value=text
        )
        embed.add_field(
            name='Datum',
            value=mail.date.strftime('%c')
        )
        embed.set_footer(text=self.bot.signature)

        return embed

    def _init_mailbox(self):
        self.mailbox = MailBox(config.iserv_hostname)
        self.mailbox.login(config.iserv_username, config.iserv_password)

    def _get_mails(self) -> List[MailMessage]:
        return list(self.mailbox.fetch(AND(to=config.target_mail, date_gte=date.today() - self.mail_date_within), bulk=True))


def setup(bot: Bot) -> None:
    bot.add_task(IservMails(bot), DefaultScheduler(120.0, bot))
    # pass
